from abc import ABC, abstractmethod
from datetime import datetime

# ==========================================
# CLASE PARA EL SISTEMA DE LOGS Y ERRORES
# ==========================================
class SistemaLogs:
    @staticmethod
    def registrar_log(mensaje, tipo="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{tipo}] {mensaje}\n"
        try:
            with open("logs.txt", "a", encoding="utf-8") as archivo:
                archivo.write(log_entry)
        except Exception as e:
            print(f"Error crítico al escribir en el log: {e}")

# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorDatoInvalido(Exception):
    pass

class ErrorReservaNoPermitida(Exception):
    pass

class ErrorClienteDuplicado(ErrorDatoInvalido):
    pass

# ==========================================
# CLASE ABSTRACTA GENERAL Y CLASE CLIENTE
# ==========================================
class EntidadSistema(ABC):
    @abstractmethod
    def mostrar_detalle(self):
        pass


class Cliente(EntidadSistema):
    cedulas_registradas = set()
    clientes_registrados = []

    def __init__(self, cedula, nombre, telefono, correo):
        
        cedula_validada = self._validar_cedula(cedula)

        if cedula_validada in Cliente.cedulas_registradas:
            SistemaLogs.registrar_log(
                f"Intento de registrar cédula duplicada: {cedula_validada}",
                "ERROR"
            )
            raise ErrorClienteDuplicado(
                "Ya existe un cliente registrado con esta cedula."
            )

        nombre_validado = self._validar_nombre(nombre)
        telefono_validado = self._validar_telefono(telefono)
        correo_validado = self._validar_correo(correo)

        self._cedula = cedula_validada
        self._nombre = nombre_validado
        self._telefono = telefono_validado
        self._correo = correo_validado

        Cliente.cedulas_registradas.add(cedula_validada)
        Cliente.clientes_registrados.append(self)

    @property
    def cedula(self):
        return self._cedula

    @property
    def nombre(self):
        return self._nombre

    @property
    def telefono(self):
        return self._telefono

    @property
    def correo(self):
        return self._correo

    def _validar_cedula(self, cedula):
        if not cedula or not str(cedula).isdigit() or len(str(cedula)) < 6:
            SistemaLogs.registrar_log(f"Intento de registrar cédula inválida: {cedula}", "ERROR")
            raise ErrorDatoInvalido("La cédula debe contener solo números y tener al menos 6 dígitos.")
        return str(cedula)

    def _validar_nombre(self, nombre):
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            SistemaLogs.registrar_log(f"Intento de registrar nombre inválido: {nombre}", "ERROR")
            raise ErrorDatoInvalido("El nombre del cliente es demasiado corto o inválido.")
        return nombre.strip()

    def _validar_telefono(self, telefono):
        telefono = str(telefono).strip()
        
        if not telefono.isdigit() or len(telefono) != 10:
            SistemaLogs.registrar_log(
                f"Telefono invalido: {telefono}", "ERROR"
            )
            raise ErrorDatoInvalido(
                "El telefono debe contener exactamente 10 digitos."
            )
        
        return telefono

    def _validar_correo(self, correo):
        if (
            not isinstance(correo, str)
            or "@" not in correo
            or "." not in correo.split("@")[-1]
            or " " in correo
        ):
            SistemaLogs.registrar_log(
                f"Correo invalido: {correo}", "ERROR"
            )
            raise ErrorDatoInvalido(
                "El correo electronico no tiene un formato valido."
            )
        
        return correo.strip()

    def mostrar_detalle(self):
        return f"Cliente: {self._nombre} (Cédula: {self._cedula})"


# ==========================================
# CLASE ABSTRACTA SERVICIO Y TRES SERVICIOS
# ==========================================
class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre_servicio, costo_base):
        if not id_servicio or not str(id_servicio).strip():
            SistemaLogs.registrar_log("ID de servicio vacío o inválido.", "ERROR")
            raise ErrorDatoInvalido("El identificador del servicio es obligatorio.")

        self._id_servicio = str(id_servicio).strip()
        self._nombre_servicio = nombre_servicio
        self._costo_base = self._validar_costo(costo_base)

    @property
    def id_servicio(self):
        return self._id_servicio

    @property
    def nombre_servicio(self):
        return self._nombre_servicio

    @property
    def costo_base(self):
        return self._costo_base

    def _validar_costo(self, costo):
        if isinstance(costo, bool) or not isinstance(costo, (int, float)) or costo < 0:
            SistemaLogs.registrar_log(f"Costo base inválido para servicio {self._id_servicio}: {costo}", "ERROR")
            raise ErrorDatoInvalido("El costo base debe ser un número mayor o igual a cero.")
        return float(costo)

    @abstractmethod
    def calcular_costo(self):
        pass

    def calcular_costo_con_opciones(self, impuesto=0.19, descuento=0.0):
        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise ErrorDatoInvalido("El impuesto debe ser un porcentaje decimal mayor o igual a 0.")
        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not (0.0 <= descuento < 1.0):
            raise ErrorDatoInvalido("El descuento debe estar entre 0.0 y menor a 1.0.")

        costo_calculado = self.calcular_costo()
        if costo_calculado < 0:
            raise ErrorDatoInvalido("El cálculo de costo resultó negativo o inconsistente.")

        costo_con_impuesto = costo_calculado * (1 + impuesto)
        costo_final = costo_con_impuesto * (1 - descuento)
        return round(costo_final, 2)


class ReservaSalas(Servicio):
    def __init__(self, id_servicio, costo_base, capacidad):
        super().__init__(id_servicio, "Reserva de Sala", costo_base)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            SistemaLogs.registrar_log(f"Capacidad inválida para sala {id_servicio}: {capacidad}", "ERROR")
            raise ErrorDatoInvalido("La capacidad de la sala debe ser un entero mayor a 0.")
        self._capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    def calcular_costo(self):
        return self._costo_base * 1.10

    def mostrar_detalle(self):
        return f"Servicio: {self._nombre_servicio} | Capacidad: {self._capacidad} personas"


class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, costo_base, horas):
        super().__init__(id_servicio, "Alquiler de Equipos", costo_base)
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0:
            SistemaLogs.registrar_log(f"Horas inválidas para alquiler {id_servicio}: {horas}", "ERROR")
            raise ErrorDatoInvalido("Las horas de alquiler deben ser un número mayor a 0.")
        self._horas = horas

    @property
    def horas(self):
        return self._horas

    def calcular_costo(self):
        return self._costo_base * self._horas

    def mostrar_detalle(self):
        return f"Servicio: {self._nombre_servicio} | Horas: {self._horas}"

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, costo_base, nivel_experto):
        super().__init__(id_servicio, "Asesoría Especializada", costo_base)
        if not isinstance(nivel_experto, bool):
            SistemaLogs.registrar_log(f"Nivel experto inválido para asesoría {id_servicio}: {nivel_experto}", "ERROR")
            raise ErrorDatoInvalido("El nivel experto debe ser un valor booleano (True o False).")
        self._nivel_experto = nivel_experto

    @property
    def nivel_experto(self):
        return self._nivel_experto

    def calcular_costo(self):
        multiplicador = 1.5 if self._nivel_experto else 1.0
        return self._costo_base * multiplicador

    def mostrar_detalle(self):
        return f"Servicio: {self._nombre_servicio} | Nivel Experto: {self._nivel_experto}"

# ==========================================
# CLASE RESERVA CON MANEJO DE EXCEPCIONES
# ==========================================
class Reserva:
    def __init__(self, cliente, servicio, duracion_dias):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            SistemaLogs.registrar_log("Intento de crear reserva con cliente o servicio inválido.", "ERROR")
            raise ErrorReservaNoPermitida("Cliente y servicio deben ser instancias válidas.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_dias = self._validar_duracion(duracion_dias)
        self._estado = "Creada"

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion_dias(self):
        return self._duracion_dias

    @property
    def estado(self):
        return self._estado

    def _validar_duracion(self, duracion):
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            SistemaLogs.registrar_log(f"Duración de reserva inválida: {duracion}", "ERROR")
            raise ErrorReservaNoPermitida("La duración de la reserva debe ser mayor a 0 días.")
        return duracion

    def confirmar_reserva(self):
        try:
            if self._estado == "Confirmada":
                raise ErrorReservaNoPermitida("La reserva ya se encuentra confirmada previamente.")
            if self._estado == "Cancelada":
                raise ErrorReservaNoPermitida("No se puede confirmar una reserva cancelada.")

            self._estado = "Confirmada"
            SistemaLogs.registrar_log(f"Reserva confirmada exitosamente para {self._cliente.nombre}")
            print(f"[ÉXITO] Reserva confirmada para el cliente {self._cliente.nombre}.")

        except ErrorReservaNoPermitida as e:
            SistemaLogs.registrar_log(f"Error al confirmar reserva: {e}", "WARNING")
            print(f"[ADVERTENCIA] No se pudo confirmar: {e}")
            raise
        except Exception as e:
            SistemaLogs.registrar_log(f"Excepción inesperada en confirmación: {e}", "CRITICAL")
            raise RuntimeError("Error crítico inesperado en el sistema.") from e
        else:
            print("[INFO] El proceso de confirmación transcurrió sin excepciones secundarias.")
        finally:
            print("[INFO] Operación de confirmación finalizada (Bloque Finally ejecutado).\n")

    def cancelar_reserva(self):
        if self._estado == "Cancelada":
            raise ErrorReservaNoPermitida("La reserva ya se encuentra cancelada previamente.")
        self._estado = "Cancelada"
        SistemaLogs.registrar_log(f"Reserva cancelada para el cliente {self._cliente.nombre}")
        print(f"[INFO] La reserva del cliente {self._cliente.nombre} ha sido cancelada.")
# ==========================================
# SIMULACIÓN DE LAS 10 OPERACIONES
# ==========================================
def ejecutar_simulacion():
    print("--- INICIANDO SIMULACIÓN DE 10 OPERACIONES ---")
    for i in range(1, 11):
        print(f"\n--- Operación simulada #{i} ---")
        try:
            if i == 1:
                c1 = Cliente("12345678", "Ana Pérez", "3200000000", "ana@mail.com")
                s1 = ReservaSalas("S01", 100000, 20)
                Reserva(c1, s1, 2).confirmar_reserva()
            elif i == 2:
                Cliente("ABC", "Carlos Ruiz", "3100000000", "carlos@mail.com")
            elif i == 3:
                AlquilerEquipos("E01", -50000, 5)
            elif i == 4:
                s2 = AlquilerEquipos("E02", 40000, 3)
                total = s2.calcular_costo_con_opciones(0.19, 0.10)
                print(f"Costo con opciones: ${total}")
            elif i == 5:
                s3 = AsesoriaEspecializada("A01", 150000, True)
                print(s3.mostrar_detalle())
                print(f"Costo asesoría: ${s3.calcular_costo()}")
            elif i == 6:
                c3 = Cliente("11223344", "María Torres", "3000000000", "maria@mail.com")
                s4 = ReservaSalas("S02", 80000, 10)
                Reserva(c3, s4, 0)
            elif i == 7:
                c4 = Cliente("99887766", "Pedro Infante", "3111111111", "pedro@mail.com")
                s5 = AlquilerEquipos("E03", 20000, 2)
                res_temp = Reserva(c4, s5, 1)
                res_temp.confirmar_reserva()
                res_temp.cancelar_reserva()
            elif i == 8:
                c5 = Cliente("55443322", "Lucía Méndez", "3222222222", "lucia@mail.com")
                s6 = AsesoriaEspecializada("A02", 200000, False)
                res_doble = Reserva(c5, s6, 3)
                res_doble.confirmar_reserva()
                res_doble.confirmar_reserva()
            elif i == 9:
                Cliente("999999", "   ", "3333333333", "espacios@mail.com")
            elif i == 10:
                cf = Cliente("77889900", "Sofía Castro", "3189999999", "sofia@mail.com")
                sf = ReservaSalas("S03", 120000, 15)
                Reserva(cf, sf, 4).confirmar_reserva()

        except (ErrorDatoInvalido, ErrorReservaNoPermitida) as e:
            print(f"[CONTROL DE EXCEPCIÓN ESPERADA]: {e}")
            SistemaLogs.registrar_log(f"Excepción controlada en op {i}: {e}", "WARNING")
        except Exception as e:
            print(f"[ERROR INESPERADO]: {e}")
            SistemaLogs.registrar_log(f"Error no controlado en op {i}: {e}", "CRITICAL")

if __name__ == "__main__":
    ejecutar_simulacion()

    print("\n--- PRUEBAS DE VALIDACION DE CONTACTO ---")

    # PRUEBA 1: TELEFONO INVALIDO
    try:
        Cliente("22334455", 
                "Juan Perez",
                "12345", 
                "juan@gmail.com"
        )
    except ErrorDatoInvalido as e:
        print(f"[ERROR CONTROLADO] {e}")

    # PRUEBA 2: CORREO INVALIDO
    try:
        Cliente("88776655", 
                "Carlos Ruiz", 
                "3100000000", 
                "correo-invalido"
        )
    except ErrorDatoInvalido as e:
        print(f"[ERROR CONTROLADO] {e}")

    # --- PRUEBA DE CEDULAS DUPLICADAS ---
print("\n--- PRUEBA DE CEDULAS DUPLICADAS ---")
    
try:
    Cliente("12345678", 
            "Cliente Duplicado", 
            "3000000000", 
            "duplicado@mail.com"
    )
except ErrorClienteDuplicado as e:
    print(f"[ERROR CONTROLADO] {e}")
