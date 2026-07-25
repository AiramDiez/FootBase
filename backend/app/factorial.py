def factorial(n: int) -> int:
    """Calcula el factorial de un número entero no negativo.

    Args:
        n (int): Número entero cuyo factorial se calcula.

    Returns:
        int: El factorial de n.

    Raises:
        ValueError: Si n es negativo.
    """
    if n < 0:
        raise ValueError("El factorial no está definido para números negativos")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


if __name__ == "__main__":
    try:
        numero = int(input("Introduce un número entero para calcular su factorial: "))
        print(f"El factorial de {numero} es {factorial(numero)}")
    except ValueError as error:
        print(f"Error: {error}")
