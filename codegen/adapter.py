from dataclasses import asdict, dataclass
from pathlib import Path
from types import FunctionType

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from codegen.common import camel2snake, create_jinja_env, parse_type


def create_adapters(interfaces: list[type], destination: Path) -> None:
    """
    Генерирует и сохраняет код адаптеров по интерфейсам.
    """
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "__init__.py").touch()

    for interface in interfaces:
        filename, adapter_str = template_adapter(interface)
        Path(destination / filename).write_text(adapter_str)


@dataclass
class Variable:
    name: str
    type: str


@dataclass
class Method:
    name: str
    return_type: str
    args: list[Variable]


@dataclass
class Adapter:
    filename: str
    imports: list[tuple[str, str]]
    class_name: str
    interface: str
    get_properties: list[Variable]
    set_properties: list[Variable]
    methods: list[Method]


def template_adapter(interface: type) -> tuple[str, str]:
    env = create_jinja_env()
    template = env.get_template("adapter.j2")
    context = _generate_template_context(interface)
    adapter_str = template.render(asdict(context))
    return context.filename, adapter_str


def _generate_template_context(interface: type) -> Adapter:
    class_name: str = interface.__name__[1:] + "Adapter"

    imports = [(cls.__module__, cls.__name__) for cls in (ICommand, IoC, UObject, interface)]
    set_properties: list[Variable] = []
    get_properties: list[Variable] = []
    methods: list[Method] = []

    for method in interface.__dict__.values():
        if not isinstance(method, FunctionType) or method.__name__.startswith("_"):
            continue

        name = method.__name__
        parsed_annotations = {
            name: parse_type(annotation) for name, annotation in method.__annotations__.items()
        }
        for pa in parsed_annotations.values():
            imports.extend(pa.imports)

        if name.startswith("get_"):
            get_properties.append(
                Variable(
                    name=name.replace("get_", ""),
                    type=parsed_annotations["return"].annotation,
                )
            )
        elif name.startswith("set_"):
            set_properties.append(
                Variable(
                    name=name.replace("set_", ""),
                    type=next(iter(parsed_annotations.values())).annotation,
                )
            )
        else:
            methods.append(
                Method(
                    name=name,
                    return_type=parsed_annotations["return"].annotation,
                    args=[
                        Variable(name=arg_name, type=arg_parsed_type.annotation)
                        for arg_name, arg_parsed_type in parsed_annotations.items()
                        if arg_name != "return"
                    ],
                )
            )

    return Adapter(
        filename=f"{camel2snake(class_name)}.py",
        imports=sorted(set(imports)),
        class_name=class_name,
        interface=interface.__name__,
        get_properties=get_properties,
        set_properties=set_properties,
        methods=methods,
    )
