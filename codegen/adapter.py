from dataclasses import asdict, dataclass
from pathlib import Path
from types import FunctionType

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.uobject import UObject
from codegen.common import camel2snake, create_jinja_env, parse_type


@dataclass
class Property:
    name: str
    type: str


@dataclass
class Adapter:
    dependencies: list[tuple[str, str]]
    class_name: str
    interface: str
    get_properties: list[Property]
    set_properties: list[Property]


def generate(interfaces: list[type], destination: Path) -> None:
    env = create_jinja_env()
    template = env.get_template("adapter.j2")

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "__init__.py").touch()

    for interface in interfaces:
        adapter = _generate_adapter(interface)
        adapter_str = template.render(asdict(adapter))
        filename = f"{camel2snake(adapter.class_name)}.py"
        Path(destination / filename).write_text(adapter_str)


def _generate_adapter(interface: type) -> Adapter:
    class_name: str = interface.__name__[1:] + "Adapter"

    dependencies = [(cls.__module__, cls.__name__) for cls in (ICommand, IoC, UObject, interface)]
    set_properties: list[Property] = []
    get_properties: list[Property] = []

    for method in interface.__dict__.values():
        if not isinstance(method, FunctionType) or method.__name__.startswith("_"):
            continue

        name = method.__name__
        parsed_annotations = {
            name: parse_type(annotation) for name, annotation in method.__annotations__.items()
        }
        for pa in parsed_annotations.values():
            dependencies.extend(pa.dependencies)

        if name.startswith("get_"):
            get_properties.append(
                Property(
                    name=name.replace("get_", ""),
                    type=parsed_annotations["return"].annotation,
                )
            )
        elif name.startswith("set_"):
            set_properties.append(
                Property(
                    name=name.replace("set_", ""),
                    type=next(iter(parsed_annotations.values())).annotation,
                )
            )

    return Adapter(
        dependencies=list(set(dependencies)),
        class_name=class_name,
        interface=interface.__name__,
        get_properties=get_properties,
        set_properties=set_properties,
    )
