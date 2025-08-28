import random

class CosmoRespuestas:
    def __init__(self):
        # Saludos iniciales
        self.saludos = [
            "¡Hola! Soy Cosmo, tu asistente personal. ¿En qué te puedo ayudar hoy?",
            "¡Hey! Aquí estoy, listo para lo que necesites.",
            "¡Qué tal! Cosmo al servicio, dime qué quieres que haga.",
            "¡Hola humano! Preparado para ayudarte en lo que necesites.",
            "El sistema está arriba y corriendo, dime en qué te ayudo."
        ]

        # Mensajes cuando está listo para recibir un comando
        self.activacion = [
            "Estoy atento. Ahora sí, dime tu comando.",
            "Listo, puedes pedirme lo que quieras.",
            "Perfecto, ya estoy escuchando tu solicitud.",
            "Aquí estoy, dime qué deseas hacer.",
            "Adelante, tu orden será escuchada."
        ]

        # Confirmaciones cuando procesa un comando
        self.confirmacion = [
            "Claro que sí, en un segundo lo hago.",
            "Perfecto, estoy trabajando en eso.",
            "Entendido, dame un momento.",
            "En marcha, tu solicitud está siendo procesada.",
            "Listo, ejecutando lo que pediste."
        ]

        # Mensajes de error o cuando no entiende
        self.error = [
            "Perdona, no entendí muy bien. ¿Podrías repetirlo?",
            "Hmm, no logré captar eso. Intenta de nuevo por favor.",
            "Creo que me perdí, ¿quieres repetir tu comando?",
            "Lo siento, no entendí tu solicitud.",
            "No logré reconocer tu comando, inténtalo otra vez."
        ]

        # Despedidas
        self.despedida = [
            "Ha sido un gusto ayudarte. ¡Hasta luego!",
            "Cierro sesión, pero aquí estaré cuando me necesites.",
            "Me desconecto por ahora. ¡Que tengas un excelente día!",
            "Nos vemos luego, cuídate mucho.",
            "Hasta pronto, vuelve cuando quieras."
        ]

    def get(self, tipo):
        """Devuelve una frase aleatoria según la categoría"""
        if tipo == "saludo":
            return random.choice(self.saludos)
        elif tipo == "activacion":
            return random.choice(self.activacion)
        elif tipo == "confirmacion":
            return random.choice(self.confirmacion)
        elif tipo == "error":
            return random.choice(self.error)
        elif tipo == "despedida":
            return random.choice(self.despedida)
        else:
            return "Lo siento, no tengo una respuesta para eso."
