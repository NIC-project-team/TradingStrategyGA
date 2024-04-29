import json
from typing import List, Any, Dict, Tuple

file_class_dict = {'Diamond': 'diamond_strategy',
                   'Strategy005': 'strategy_005',
                   'PatternRecognition': 'pattern_recognition_strategy',
                   'SampleStrategy': 'sample_strategy'}


def generate_text(strategy_class: str, parameters: Dict[Any, Dict], file_num: int, default_spaces: bool = False) -> Tuple[str, str]:
    """ Generates a text representation of a strategy class that extends the class with custom hyperopt search spaces
    and search spaces for custom parameters
    :param strategy_class: name of the strategy class
    :param parameters: dictionary of parameters and their values
    :param file_num: number of the file
    :param default_spaces: if True, adds default search spaces for stoploss and ROI
    :return: text representation of the class, filename
    """
    text = f"from typing import Type, List, Any, Dict\n"
    text += f"from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy\n"
    text += f"from {file_class_dict[strategy_class]} import {strategy_class}\n\n\n"
    text += f"class New{strategy_class}{file_num}({strategy_class}):\n"

    # changing default search spaces
    if default_spaces:
        text += f"    class HyperOpt:\n"
        text += f"        # Define a custom stoploss space.\n"
        text += f"        def stoploss_space(self):\n"
        text += f"            return [SKDecimal(-0.05, -0.01, decimals=3, name='stoploss')]\n\n"
        text += f"        # Define custom ROI space\n"
        text += f"        def roi_space(self) -> List[Dimension]:\n"
        text += f"            return [\n"
        text += f"                Integer(10, 120, name='roi_t1'),\n"
        text += f"                Integer(10, 60, name='roi_t2'),\n"
        text += f"                Integer(10, 40, name='roi_t3'),\n"
        text += f"                SKDecimal(0.01, 0.04, decimals=3, name='roi_p1'),\n"
        text += f"                SKDecimal(0.01, 0.07, decimals=3, name='roi_p2'),\n"
        text += f"                SKDecimal(0.01, 0.20, decimals=3, name='roi_p3'),\n"
        text += f"            ]\n\n"
        text += f"        def generate_roi_table(self, params: Dict) -> Dict[int, float]:\n"
        text += f"            roi_table = {{}}\n"
        text += f"            roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']\n"
        text += f"            roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']\n"
        text += f"            roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']\n"
        text += f"            roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0\n\n"
        text += f"            return roi_table\n"

    # adding custom parameters to the strategy
    for parameter in parameters:
        if parameter == 'loss':
            continue
        values = parameters[parameter]

        if values['type'] == 'int':
            text += (f"        {parameter} = IntParameter(low={int(values['low'])}, high={int(values['high'])}, "
                     f"default={values['default']}, space='{values['space']}', optimize=True)\n")

        elif values['type'] == 'float':
            text += (f"        {parameter} = DecimalParameter(low={values['low']}, high={values['high']}, "
                     f"decimals={values['decimals']}, default={values['default']}, space='{values['space']}', optimize=True)\n")

        elif values['type'] == 'categorical':
            # if default is a string representing a number, convert it to an int
            if values['default'].isdigit():
                text += (
                    f"        {parameter} = CategoricalParameter({values['options']}, default={values['default']}, "
                    f"space='{values['space']}', optimize=True)\n")
            else:
                text += (
                    f"        {parameter} = CategoricalParameter({values['options']}, default='{values['default']}', "
                    f"space='{values['space']}', optimize=True)\n")

        elif values['type'] == 'boolean':
            text += (f"        {parameter} = BooleanParameter(default={values['default']}, space='{values['space']}', optimize=True)\n")

    text += f"\n"
    filename = f"user_data/strategies/new_{file_class_dict[strategy_class]}.py"

    with open(filename, "w") as file:
        file.write(text)

    return text, filename


def get_parameter(line: str) -> Tuple[str, List[str]]:
    """ Parse a line of a strategy file and return the parameter name and its values
    Parameters:
        line: str
    Returns:
        parameter_name: string of the parameter name;
        parameter_vals: list of parameter values
    """
    if "[" in line:
        parameter_name = line.split()[0]
        parameter_vals_options = line.split("[")[1].split("]")[0]
        parameter_vals_options = parameter_vals_options.split(", ")
        parameter_vals_options = [val.split("=")[-1].replace("'", "").replace(" ", "") for val in parameter_vals_options]
        parameter_vals = [parameter_vals_options]

        line = line.replace(f'{parameter_vals_options}, ', "")
        parameter_vals += line.split("(")[1].split(")")[0].split(", ")

        for i in range(1, 3):
            if "=" in parameter_vals[i]:
                parameter_vals[i] = parameter_vals[i].split("=")[-1].replace("'", "").replace(" ", "")

        return parameter_name, parameter_vals
    else:
        parameter_name = line.split()[0]
        parameter_vals = line.split("(")[1].split(")")[0]
        parameter_vals = parameter_vals.split(", ")
        parameter_vals = [val.split("=")[-1].replace("'", "").replace(" ", "") for val in parameter_vals]

        return parameter_name, parameter_vals


def parse_parameters(strategy_file: str) -> Tuple[Dict[str, Dict], str]:
    """ Parse a strategy file and return a dictionary of parameters and their values
    Parameters:
        strategy_file: str
    Returns:
        parameters: dict of parameters and their values;
        timeframe: str
    """
    with open(strategy_file, "r") as file:
        lines = file.readlines()
    parameters = {}
    timeframe = '1h'
    for line in lines:
        if "Parameter" in line:
            if 'from freqtrade.strategy import ' in line:
                continue

            if "DecimalParameter" in line or "IntParameter" in line:
                parameter_name, parameter_vals = get_parameter(line)
                type_param = "int" if "IntParameter" in line else "float"
                parameters[parameter_name] = {'type': type_param,
                                              'low': float(parameter_vals[0]),
                                              'high': float(parameter_vals[1]),
                                              'default': float(parameter_vals[2]),
                                              'space': parameter_vals[3]}

                if type_param == "float":
                    parameters[parameter_name]['decimals'] = int(parameter_vals[2])
                    parameters[parameter_name]['space'] = parameter_vals[4]

            elif "CategoricalParameter" in line:
                parameter_name, parameter_vals = get_parameter(line)
                type_param = "categorical"
                parameters[parameter_name] = {'type': type_param,
                                                'options': parameter_vals[0],
                                                'default': parameter_vals[1],
                                                'space': parameter_vals[2]}

            elif "BooleanParameter" in line:
                parameter_name, parameter_vals = get_parameter(line)
                type_param = "boolean"
                parameters[parameter_name] = {'type': type_param,
                                              'default': parameter_vals[0],
                                              'space': parameter_vals[1]}

        if 'timeframe = ' in line:
            timeframe = line.split('=')[-1].strip().replace("'", "").replace('"', "")

    return parameters, timeframe


def parse_report(filename):
    """Get losses of the best candidates, average losses in population, the best candidates and final time from a report
    file.
    Parameters:
         filename: str
    Returns:
        losses: list of losses of the best candidates;
        avg_losses: list of average losses in population;
        best_candidates: list of the best candidates;
        final_time: str of the final time
    """
    with open(filename) as f:
        data = json.load(f)

    losses = data['losses']
    avg_losses = data['avg_losses']
    best_candidates = data['best_candidates']
    final_time = data['final_time']

    return losses, avg_losses, best_candidates, final_time


def generate_classes_from_report(report_file, strategy_class):
    """Generate classes from a report file (best candidates classes)
    Parameters:
        report_file: str
        strategy_class: str
    """
    _, _, best_candidates, _ = parse_report(report_file)

    for i, candidate in enumerate(best_candidates):
        with open(f"user_data/strategies/new_{strategy_class}{i}.py", "w") as file:
            text, filename = generate_text(strategy_class, candidate, i)
            file.write(text)

        print(text)
        print(filename)


if __name__ == "__main__":
    # strategy_class = "Strategy005"
    # strategy_file = 'user_data/strategies/sample_strategy.py'
    # strategy_params, timeframe = parse_parameters(strategy_file)
    # text, filename = generate_text(strategy_class, strategy_params, 0)
    # print(text)

    generate_classes_from_report('reports/Diamond.json', 'Diamond')
