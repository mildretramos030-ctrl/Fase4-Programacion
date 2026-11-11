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

# ==========================================
# CLASE ABSTRACTA GENERAL Y CLASE CLIENTE
# ==========================================
class EntidadSistema(ABC):
    @abstractmethod
    def mostrar_detalle(self):
        pass

class Cliente(EntidadSistema):
    def __init__(self, cedula, nombre, telefono, correo):
        self.cedula = self._validar_cedula(cedula)
        self.nombre = self._validar_nombre(nombre)
        self.telefono = telefono
        self.correo = correo

    def _validar_cedula(self, cedula):
        if not cedula or not str(cedula).isdigit() or len(str(cedula)) < 6:
            SistemaLogs.registrar_log(f"Intento de registrar cédula inválida: {cedula}", "ERROR")
            raise ErrorDatoInvalido("La cédula debe contener solo números y tener al menos 6 dígitos.")
        return str(cedula)

    def _validar_nombre(self, nombre):
        if not nombre or len(nombre.strip()) < 3:
            SistemaLogs.registrar_log(f"Intento de registrar nombre inválido: {nombre}", "ERROR")
            raise ErrorDatoInvalido("El nombre del cliente es demasiado corto o inválido.")
        return nombre.strip()

    def mostrar_detalle(self):
        return f"Cliente: {self.nombre} (Cédula: {self.cedula})"

# ==========================================
# CLASE ABSTRACTA SERVICIO Y TRES SERVICIOS
# ==========================================
class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre_servicio, costo_base):
        self.id_servicio = id_servicio
        self.nombre_servicio = nombre_servicio
        self.costo_base = self._validar_costo(costo_base)

    def _validar_costo(self, costo):
        if costo < 0:
            SistemaLogs.registrar_log(f"Costo base negativo para servicio {self.id_servicio}", "ERROR")
            raise ErrorDatoInvalido("El costo base no puede ser negativo.")
        return costo

    @abstractmethod
    def calcular_costo(self):
        pass

    def calcular_costo_con_opciones(self, impuesto=0.19, descuento=0.0):
        costo_calculado = self.calcular_costo()
        costo_con_impuesto = costo_calculado * (1 + impuesto)
        costo_final = costo_con_impuesto * (1 - descuento)
        return round(costo_final, 2)

class ReservaSalas(Servicio):
    def __init__(self, id_servicio, costo_base, capacidad):
        super().__init__(id_servicio, "Reserva de Sala", costo_base)
        self.capacidad = capacidad

    def calcular_costo(self):
        return self.costo_base * 1.10

    def mostrar_detalle(self):
        return f"Servicio: {self.nombre_servicio} | Capacidad: {self.capacidad} personas"

class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, costo_base, horas):
        super().__init__(id_servicio, "Alquiler de Equipos", costo_base)
        self.horas = horas

    def calcular_costo(self):
        return self.costo_base * self.horas

    def mostrar_detalle(self):
        return f"Servicio: {self.nombre_servicio} | Horas: {self.horas}"

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, costo_base, nivel_experto):
        super().__init__(id_servicio, "Asesoría Especializada", costo_base)
        self.nivel_experto = nivel_experto

    def calcular_costo(self):
        multiplicador = 1.5 if self.nivel_experto else 1.0
        return self.costo_base * multiplicador

    def mostrar_detalle(self):
        return f"Servicio: {self.nombre_servicio} | Nivel Experto: {self.nivel_experto}"

# ==========================================
# CLASE RESERVA CON MANEJO DE EXCEPCIONES
# ==========================================
class Reserva:
    def __init__(self, cliente, servicio, duracion_dias):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_dias = self._validar_duracion(duracion_dias)
        self.estado = "Creada"

    def _validar_duracion(self, duracion):
        if duracion <= 0:
            SistemaLogs.registrar_log(f"Duración de reserva inválida: {duracion}", "ERROR")
            raise ErrorReservaNoPermitida("La duración de la reserva debe ser mayor a 0 días.")
        return duracion

    def confirmar_reserva(self):
        try:
            if self.estado == "Confirmada":
                raise ErrorReservaNoPermitida("La reserva ya se encuentra confirmada previamente.")
            
            self.estado = "Confirmada"
            SistemaLogs.registrar_log(f"Reserva confirmada exitosamente para {self.cliente.nombre}")
            print(f"[ÉXITO] Reserva confirmada para el cliente {self.cliente.nombre}.")

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
        self.estado = "Cancelada"
        SistemaLogs.registrar_log(f"Reserva cancelada para el cliente {self.cliente.nombre}")
        print(f"[INFO] La reserva del cliente {self.cliente.nombre} ha sido cancelada.")

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
                print(f"Costo con sobrecarga: ${total}")
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
                res_Doble = Reserva(c5, s6, 3)
                res_Doble.confirmar_reserva()
                res_Doble.confirmar_reserva()
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