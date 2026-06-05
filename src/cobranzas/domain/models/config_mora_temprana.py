from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigMoraTemprana:
    dias_min: int
    dias_max: int
    estados_excluidos: tuple[str, ...]
    tipos_oper_excluidos: tuple[str, ...]
    origen: str = "env"
