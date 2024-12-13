import numpy as np
import pandas as pd


class HopfieldNetwork:
    def __init__(self, weight_matrix):
        """
        Initialize the Hopfield Network with a given weight matrix.
        :param weight_matrix: 2D numpy array (square matrix)
        """
        self.weight_matrix = np.array(weight_matrix)
        self.num_neurons = self.weight_matrix.shape[0]

    def sign_function(self, x):
        """
        Activation function for the Hopfield network.
        :param x: Input value
        :return: +1 if x >= 0, -1 otherwise
        """
        return np.where(x >= 0, 1, -1)

    def update(self, state, synchronous=True):
        """
        Update the state of the Hopfield network.
        :param state: Current state vector
        :param synchronous: Boolean to determine if updates are synchronous or asynchronous
        :return: Updated state vector
        """
        if synchronous:
            # Synchronous update: All neurons updated at once
            new_state = self.sign_function(np.dot(self.weight_matrix, state))
        else:
            # Asynchronous update: Update neurons one at a time
            new_state = state.copy()
            for i in range(self.num_neurons):
                new_state[i] = self.sign_function(np.dot(self.weight_matrix[i], state))
        return new_state

    def run(self, initial_state, max_iterations=100, synchronous=True):
        """
        Run the Hopfield network until convergence or for a maximum number of iterations.
        :param initial_state: Initial state vector
        :param max_iterations: Maximum number of iterations
        :param synchronous: Boolean to determine if updates are synchronous or asynchronous
        :return: Final state vector
        """
        state = np.array(initial_state)
        for _ in range(max_iterations):
            new_state = self.update(state, synchronous=synchronous)
            if np.array_equal(new_state, state):  # Check for convergence
                break
            state = new_state
        return state



# Load the CSV as a DataFrame
# Assume the CSV file is named 'data.csv' and has headers 'x' and 'y'
df = pd.read_csv('matrix_output.csv')


# Remove the first column (gene names)
df = df.iloc[:, 1:]
# Replace 'x' values with 0 in the entire DataFrame
df.replace('x', 0, inplace=True)
print(df)
# Convert the DataFrame to a NumPy matrix
weight_matrix = df.to_numpy()

#
# ###TEST
# def create_hopfield_weight_matrix(patterns):
#     """
#     Create a Hopfield network weight matrix using Hebbian learning.
#     :param patterns: List of binary patterns (e.g., +1/-1) to store in the network
#     :return: Weight matrix
#     """
#     num_neurons = len(patterns[0])
#     weight_matrix = np.zeros((num_neurons, num_neurons))
#
#     # Hebbian learning: Sum outer products of patterns
#     for pattern in patterns:
#         pattern = np.array(pattern)
#         weight_matrix += np.outer(pattern, pattern)
#
#     # Ensure diagonal weights are zero
#     np.fill_diagonal(weight_matrix, 0)
#     return weight_matrix / len(patterns)  # Normalize by the number of patterns
#
#
# # Example usage:
# # Generate random patterns of length 20
# num_neurons = 20
# num_patterns = 5
# patterns = [np.random.choice([-1, 1], size=num_neurons) for _ in range(num_patterns)]
#
# # Create the weight matrix
# weight_matrix = create_hopfield_weight_matrix(patterns)
#

# Initialize the Hopfield network
hopfield_net = HopfieldNetwork(weight_matrix)

# Define the initial state
initial_state = np.random.randn(weight_matrix.shape[0])

# Run the Hopfield network
final_state = hopfield_net.run(initial_state, max_iterations=10, synchronous=True)
print("Final state:", final_state)

import matplotlib.pyplot as plt

def plot_state_evolution(state_history):
    """
    Plots the evolution of the Hopfield network's states.
    :param state_history: List of state vectors over iterations
    """
    state_history = np.array(state_history)
    plt.figure(figsize=(10, 6))
    plt.imshow(state_history.T, cmap='binary', aspect='auto', interpolation='nearest')
    plt.colorbar(label="State (-1 or 1)")
    plt.xlabel("Iteration")
    plt.ylabel("Neuron Index")
    plt.title("State Evolution in Hopfield Network")
    plt.show()

# Example usage:
# Track state history
state_history = []
state = initial_state
for _ in range(30):
    state_history.append(state)
    state = hopfield_net.update(state, synchronous=True)

# Visualize state evolution
plot_state_evolution(state_history)

def calculate_energy(weight_matrix, state):
    """
    Calculate the energy of the Hopfield network.
    :param weight_matrix: Weight matrix of the network
    :param state: Current state vector
    :return: Energy value
    """
    state = np.array(state)
    return -0.5 * np.dot(state.T, np.dot(weight_matrix, state))

def plot_energy_evolution(weight_matrix, state_history):
    """
    Plots the energy evolution of the Hopfield network.
    :param weight_matrix: Weight matrix of the network
    :param state_history: List of state vectors over iterations
    """
    energies = [calculate_energy(weight_matrix, state) for state in state_history]
    plt.figure(figsize=(8, 5))
    plt.plot(energies, marker='o', linestyle='-')
    plt.xlabel("Iteration")
    plt.ylabel("Energy")
    plt.title("Energy Evolution in Hopfield Network")
    plt.grid()
    plt.show()

# Example usage:
plot_energy_evolution(weight_matrix, state_history)


def visualize_patterns(initial_pattern, final_pattern):
    """
    Visualizes the input and output patterns of the Hopfield network.
    :param initial_pattern: Initial (noisy) pattern
    :param final_pattern: Final (recalled) pattern
    """
    plt.figure(figsize=(8, 4))

    # Initial pattern
    plt.subplot(1, 2, 1)
    plt.title("Initial Pattern")
    plt.imshow(initial_pattern, cmap='binary')
    plt.axis('off')

    # Final pattern
    plt.subplot(1, 2, 2)
    plt.title("Final Pattern")
    plt.imshow(final_pattern, cmap='binary')
    plt.axis('off')

    plt.show()

