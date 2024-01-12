import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble

def shor_algorithm(N):
    # Стъпка 1: Избор на произволно цяло число в интервала от 2 до N-1
    a = np.random.randint(2, N - 1)

    # Стъпка 2: Използване на класически алгоритми за намиране на GCD на a и N
    gcd_value = np.gcd(a, N)
    if gcd_value > 1:
        # Nontrivial factor found, return it
        return gcd_value

    # Стъпка 3: Намиране на квантовия период
    quantum_circuit = create_shor_circuit(a, N)
    result = run_quantum_circuit(quantum_circuit)

    # Стъпка 4: Класическа последваща обработка за намиране на периодите
    factors = find_factors(result, N)

    return factors

def create_shor_circuit(a, N):
    # Квантова верига за намиране на период
    num_qubits = 2 * int(np.ceil(np.log2(N)))
    quantum_circuit = QuantumCircuit(num_qubits, num_qubits)

    # Прилагане на портите на Адамар за първия регистър
    quantum_circuit.h(range(num_qubits // 2))

    # Прилагане на контролирани U операции
    for q in range(num_qubits // 2):
        quantum_circuit.append(c_amod15(a, 2 ** q, N), 
                               [q] + [i + num_qubits // 2 for i in range(num_qubits // 2)])
    # Прилагане на обратно квантово преобразуване на Фурие
    quantum_circuit.append(qft_dagger(num_qubits // 2), range(num_qubits // 2))

    # Пресмятане на първия регистър
    quantum_circuit.measure(range(num_qubits // 2), range(num_qubits // 2))
    return quantum_circuit

def run_quantum_circuit(quantum_circuit):
    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(quantum_circuit, simulator)
    result = simulator.run(assemble(compiled_circuit)).result()
    counts = result.get_counts()

    return counts

def find_factors(counts, N):
    # Намиране на най-вероятния резултат от преброяването
    measured_value = max(counts, key=counts.get)

    # Преобразуване на измерената стойност в цяло число
    measured_int = int(measured_value, 2)

    # Намиране на множителите чрез използване на непрекъснати дроби
    factors = np.gcd(measured_int, N), np.gcd((measured_int + 2) % N, N)

    return factors

# Помощни функции за квантови операции
def c_amod15(a, power, N):
    # Контролирано умножение с mod 15
    U = QuantumCircuit(4)
    for iteration in range(power):
        U.swap(2, 3)
        U.swap(1, 2)
        U.swap(0, 1)
        U.x(0)
        U.x(2)
        U.x(3)
        U.mcx([0, 1, 2], 3)
        U.x(0)
        U.x(2)
        U.x(3)
    U = U.to_gate()
    U.name = "U^%d mod 15" % power
    c_U = U.control()
    return c_U

def qft_dagger(n):
    # Обратно квантово преобразуване на Фурие върху n кубита
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

# Пример
number_to_factorize = 21
result = shor_algorithm(number_to_factorize)
print(f"Factors of {number_to_factorize}: {result}")