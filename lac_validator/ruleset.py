# TODO implement update registry as function here https://github.com/data-to-insight/quality-lac-data-beta-validator/pull/648#discussion_r1224480979

from lac_validator.rule_engine import registry

ruleset_updates = {}
ruleset_years = []

# get rulesets for each year as a dictionary. Chronological order should be maintained.

# 2022_23
import lac_validator.rules.lac2022_23

lac22_23 = registry.to_dict()
ruleset_updates["lac2022_23"] = {"deleted": [], "ruleset": lac22_23}
ruleset_years.append("lac2022_23")
registry.reset()

# 2023_24
# add code block to get rules for the next year here.


# Create customised registry object based on year specified.
def create_registry(ruleset=ruleset_years[-1]):
    """
    :param str ruleset: year whose version of rules should be run. e.g cin2022_23.
    Defaults to latest recorded year.
    """

    chosen_ruleset_ind = ruleset_years.index(ruleset)

    # the 2022_23 ruleset will always be the starting point.
    combined_ruleset = ruleset_updates["lac2022_23"]["ruleset"]

    # loop starts from position 1 because cin2022_23 is in position 0.
    # offset by 1 to ensure that the chosen ruleset is included.
    for year in ruleset_years[1 : chosen_ruleset_ind + 1]:
        year_update = ruleset_updates[year]

        # delete specified rules as specified by their rules codes.
        for deleted_rule in year_update["deleted"]:
            combined_ruleset.pop(deleted_rule, None)

        # incorporate rule updates and new rules.
        combined_ruleset = combined_ruleset | year_update["ruleset"]

    registry.add_ruleset(combined_ruleset)

    return registry
