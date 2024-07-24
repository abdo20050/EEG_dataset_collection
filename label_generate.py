import random

def generate_labels(max_occurrences = 100, labels = [1, 2, 3, 4]):
    # Define your list of labels and their respective maximum occurrences
    # labels = ['right', 'left', 'forward', 'backward']
    

    # Initialize variables
    occurrences = {label: 0 for label in labels}
    last_label = None

    def get_next_label():
        nonlocal last_label

        # Generate random sequence of labels
        while sum(occurrences.values()) < len(labels) * max_occurrences:
            # Calculate probabilities based on occurrences
            probabilities = [1 / (occurrences[label] + 1) for label in labels]

            # Normalize probabilities to sum to 1
            total_probability = sum(probabilities)
            probabilities = [prob / total_probability for prob in probabilities]

            # Choose a label based on probabilities
            label = random.choices(labels, probabilities)[0]

            # Check if the label can be added
            if label != last_label and occurrences[label] < max_occurrences:
                occurrences[label] += 1
                last_label = label
                return label

    return get_next_label
if __name__ == "__main__":

    # Create a label generator
    label_generator = generate_labels(100)

    # Call the function to get the next label
    for _ in range(20):
        next_label = label_generator()
        print(next_label)
        # print(type(next_label))
