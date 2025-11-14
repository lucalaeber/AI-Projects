import pandas as pd

class VariableElimination:
    """
    Implements the Variable Elimination algorithm for Bayesian networks.
    """
    def __init__(self, network):
        """
        Initialize the variable elimination algorithm with the specified network.
        Add more initializations if necessary.

        """
        self.network = network
        self.logs = []

    def log(self, message):
        """
        Adding a log message to the log file
        """
        self.logs.append(message)

    def save_logs(self, filepath='variable_elimination_log.txt'):
        """
        Save the collected logs to a text file
        """
        with open(filepath, 'w') as file:
            for log in self.logs:
                file.write(log + '\n')

    def reduce(self, factor, variable, value):
        """
        Reduces the factor by fixing a specific variable to a given value.
        Removes the fixed variable from the scope and filters rows in the data.
        Returns the reduced factor.
        """
        if variable not in factor.columns:
            return factor

        reduced_data = factor[factor[variable] == value]
        reduced_data = reduced_data.drop(columns=[variable])
        return reduced_data

    def marginalize(self, factor, variable):
        """
        Eliminates a variable by summing out its probabilities.
        Groups the data by all variables except the one being eliminated.
        Returns the marginalized factor.
        """
        if variable not in factor.columns:
            return factor

        marginalized_factor = factor.drop(columns=[variable])
        marginalized_factor = marginalized_factor.groupby(list(marginalized_factor.columns[:-1])).sum().reset_index()
        return marginalized_factor

    def product(self, factor1, factor2):
        """
        Multiplies two factors by merging their data on the common variables
        and computing the new probabilities by multiplying corresponding rows.
        Returns the resulting factor.
        """
        common_vars = list(set(factor1.columns) & set(factor2.columns) - {'prob'})

        if not common_vars:
            factor1['key'] = 1
            factor2['key'] = 1
            merged_factor = pd.merge(factor1, factor2, on='key', how='outer').drop(columns=['key'])
        else:
            merged_factor = pd.merge(factor1, factor2, on=common_vars, how='outer')

        merged_factor['prob'] = merged_factor['prob_x'] * merged_factor['prob_y']
        merged_factor = merged_factor.drop(columns=['prob_x', 'prob_y'])
        return merged_factor

    def run(self, query, observed, elim_order):
        """
        Use the variable elimination algorithm to find out the probability
        distribution of the query variable given the observed variables.

        Input:
            query:      The query variable
            observed:   A dictionary of the observed variables {variable: value}
            elim_order: A list specifying the elimination ordering

        Output: A variable holding the probability distribution for the query variable.
        """
        self.log(f"Query: {query}")
        self.log(f"Observed: {observed}")
        self.log(f"Elimination Order: {elim_order}")

        factors = list(self.network.probabilities.values())

        # Apply evidence to the factors
        for var, value in observed.items():
            updated_factors = []
            for factor in factors:
                reduced_factor = self.reduce(factor, var, value)
                updated_factors.append(reduced_factor)
            factors = updated_factors
            self.log(f"Factors after applying evidence {var}={value}: {factors}")

        # Process elimination order
        for var in elim_order:
            if var in observed or var == query:
                continue

            relevant_factors = [factor for factor in factors if var in factor.columns]

            if not relevant_factors:
                continue

            self.log(f"Relevant factors for {var}: {relevant_factors}")

            combined_factor = relevant_factors[0]
            for factor in relevant_factors[1:]:
                combined_factor = self.product(combined_factor, factor)

            self.log(f"Factor after combining for {var}: {combined_factor}")

            marginalized_factor = self.marginalize(combined_factor, var)
            self.log(f"Factor after marginalizing {var}: {marginalized_factor}")

            factors = [factor for factor in factors if not any(factor.equals(relevant) for relevant in relevant_factors)]
            factors.append(marginalized_factor)

        # Combine remaining factors
        final_factor = factors[0]
        for factor in factors[1:]:
            final_factor = self.product(final_factor, factor)

        self.log(f"Final combined factor: {final_factor}")

        # Normalize the final factor
        final_factor['prob'] /= final_factor['prob'].sum()
        self.log(f"Normalized final factor: {final_factor}")

        self.save_logs()
        return final_factor.loc[:, [query, 'prob']]
