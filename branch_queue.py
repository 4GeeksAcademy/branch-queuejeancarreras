from collections import deque
from dataclasses import dataclass
from datetime import datetime
from threading import Lock


SERVICE_TYPES = ("deposito", "retiro", "gestion_cuenta")


@dataclass(frozen=True)
class Ticket:
    number: int
    client_name: str
    service_type: str
    issued_at: datetime


class QueueEmptyError(LookupError):
    """Raised when an agent requests a customer from an empty queue."""


class BranchQueue:
    def __init__(self) -> None:
        self._queues = {service: deque() for service in SERVICE_TYPES}
        self._queue_locks = {service: Lock() for service in SERVICE_TYPES}
        self._next_number = 1
        self._number_lock = Lock()

    @staticmethod
    def _validate_service(service_type: str) -> None:
        if not isinstance(service_type, str) or service_type not in SERVICE_TYPES:
            allowed = ", ".join(SERVICE_TYPES)
            raise ValueError(f"Tipo de servicio inválido. Usa: {allowed}.")

    def issue_ticket(self, client_name: str, service_type: str) -> Ticket:
        self._validate_service(service_type)
        client_name = client_name.strip()
        if not client_name:
            raise ValueError("El nombre del cliente no puede estar vacío.")

        with self._number_lock:
            ticket = Ticket(
                number=self._next_number,
                client_name=client_name,
                service_type=service_type,
                issued_at=datetime.now(),
            )
            with self._queue_locks[service_type]:
                self._queues[service_type].append(ticket)
                self._next_number += 1
        return ticket

    def call_next(self, service_type: str) -> Ticket:
        self._validate_service(service_type)
        with self._queue_locks[service_type]:
            if not self._queues[service_type]:
                raise QueueEmptyError(
                    f"No hay clientes esperando para {service_type}."
                )
            return self._queues[service_type].popleft()

    def peek_next(self, service_type: str) -> Ticket:
        self._validate_service(service_type)
        with self._queue_locks[service_type]:
            if not self._queues[service_type]:
                raise QueueEmptyError(
                    f"No hay clientes esperando para {service_type}."
                )
            return self._queues[service_type][0]

    def list_waiting(self) -> dict[str, list[Ticket]]:
        waiting = {}
        for service in SERVICE_TYPES:
            with self._queue_locks[service]:
                waiting[service] = list(self._queues[service])
        return waiting

    def stats(self) -> dict[str, int]:
        counts = {}
        for service in SERVICE_TYPES:
            with self._queue_locks[service]:
                counts[service] = len(self._queues[service])
        counts["total"] = sum(counts.values())
        return counts


def main() -> int:
    branch = BranchQueue()
    while True:
        print("\n=== Banco Meridional: gestor de colas ===")
        print("1. Emitir ticket")
        print("2. Llamar al siguiente cliente")
        print("3. Listar clientes en espera")
        print("4. Ver estadísticas")
        print("5. Salir")

        try:
            choice = input("Selecciona una opción: ").strip()
            if choice == "1":
                client_name = input("Nombre del cliente: ").strip()
                service_type = input(
                    f"Servicio ({', '.join(SERVICE_TYPES)}): "
                ).strip()
                ticket = branch.issue_ticket(client_name, service_type)
                print(
                    f"Ticket #{ticket.number} emitido para {ticket.client_name} "
                    f"({ticket.service_type}) a las "
                    f"{ticket.issued_at.isoformat(timespec='seconds')}."
                )
            elif choice == "2":
                service_type = input(
                    f"Servicio ({', '.join(SERVICE_TYPES)}): "
                ).strip()
                ticket = branch.call_next(service_type)
                print(
                    f"Siguiente: ticket #{ticket.number}, {ticket.client_name} "
                    f"({ticket.service_type})."
                )
            elif choice == "3":
                for service, tickets in branch.list_waiting().items():
                    print(f"\n{service}:")
                    if tickets:
                        for ticket in tickets:
                            print(f"  #{ticket.number} - {ticket.client_name}")
                    else:
                        print("  Sin clientes en espera.")
            elif choice == "4":
                counts = branch.stats()
                for service in SERVICE_TYPES:
                    print(f"{service}: {counts[service]}")
                print(f"Total: {counts['total']}")
            elif choice == "5":
                print("Hasta luego.")
                return 0
            else:
                print("Opción inválida. Elige un número del 1 al 5.")
        except (ValueError, LookupError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del gestor de colas.")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
def main() -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())