import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble


def shor_algorithm(N):
    # Step 1: Choose a random integer a between 2 and N-1
    a = np.random.randint(2, N - 1)

    # Step 2: Use classical algorithms to find the GCD of a and N
    gcd_value = np.gcd(a, N)
    if gcd_value > 1:
        # Nontrivial factor found, return it
        return gcd_value

    # Step 3: Quantum period finding
    quantum_circuit = create_shor_circuit(a, N)
    result = run_quantum_circuit(quantum_circuit)

    # Step 4: Classical post-processing to find factors
    factors = find_factors(result, N)

    return factors


def create_shor_circuit(a, N):
    # Quantum circuit for period finding
    num_qubits = 2 * int(np.ceil(np.log2(N)))

    quantum_circuit = QuantumCircuit(num_qubits, num_qubits)

    # Apply Hadamard gates to the first register
    quantum_circuit.h(range(num_qubits // 2))

    # Apply controlled-U operations
    for q in range(num_qubits // 2):
        quantum_circuit.append(c_amod15(a, 2 ** q, N),
                               [q] + [i + num_qubits // 2 for i in range(num_qubits // 2)])

    # Apply inverse Quantum Fourier Transform
    quantum_circuit.append(qft_dagger(num_qubits // 2), range(num_qubits // 2))

    # Measure the first register
    quantum_circuit.measure(range(num_qubits // 2), range(num_qubits // 2))

    return quantum_circuit


def run_quantum_circuit(quantum_circuit):
    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(quantum_circuit, simulator)
    result = simulator.run(assemble(compiled_circuit)).result()
    counts = result.get_counts()

    return counts


def find_factors(counts, N):
    # Find the most probable result from the counts
    measured_value = max(counts, key=counts.get)

    # Convert the measured value to an integer
    measured_int = int(measured_value, 2)

    # Find factors using continued fractions
    factors = np.gcd(measured_int, N), np.gcd((measured_int + 2) % N, N)

    return factors


# Helper functions for quantum operations
def c_amod15(a, power, N):
    # Controlled multiplication by a mod 15
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
    # Inverse Quantum Fourier Transform on n qubits
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc


# Example usage
number_to_factorize = 18
result = shor_algorithm(number_to_factorize)
print(f"Factors of {number_to_factorize}: {result}")
