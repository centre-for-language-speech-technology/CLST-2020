# Python script to read in different result files and output one excel file containing all the relevant information
# Created by Maarten Vos s4385527
from __future__ import print_function
import glob
import pandas as pd
import re


def create_dataframe():
    """
    Create a dataframe in which all the data is stored
    :return: The dataframe that is created
    """
    columns = ['type', 'file_name', "duur_tot", 'tot_int', 'expression', 'nr_undefined', 'dur_mean', 'pitch_min_mean',
                'pitch_max_mean', 'pitch_mean_mean', 'pitch_std_mean', 'pitch_var_mean',
                'intensity_min_mean', 'intensity_max_mean', 'intensity_mean_mean', 'intensity_std_mean', 'f0_mean',
                'f1_mean', 'f2_mean', 'f3_mean', 'grav_center_mean']
    return pd.DataFrame(columns=columns)


def extract_from_results(file_name):
    """
    Extract the relevant information from the result file
    :param nr: The name of the current file
    :return: A list containing the extracted features from the file
    """
    # Read in the lines of the current file
    with open(file_name, "r") as f:
        lines = f.readlines()

        # Determine the type of the recording (stable, exacerbation, reference)
        type = file_name.split('_')[1][:-5]

        # Create a list containing for each element in the file a dictionary
        dict_list = [{} for _ in range(len(lines[2:]))]

        for i, line in enumerate(lines[2:]):

            # Split the line into an easy to use list
            line_list = line.split(" ")

            # Use the row dict in which all the information for the current row is stored
            row_dict = dict_list[i]

            # Add the type to the list
            row_dict['type'] = type

            # Add the name of the file from which the information is extracted
            row_dict['file_name'] = line_list[0]

            # Add the total duration
            row_dict["duur_tot"] = int(line_list[-1])

            # Add the number of intervals
            row_dict['tot_int'] = int(line_list[-3])


            # Extract the expression that is said and how many of the measurements are not defined
            nr_und = 0
            means = [0 for _ in range(15)]  # duration, pitch min max mean std var,
                                                 # intensity min max mean std, f0, f1, f2, f3, grav
            nr_means = means.copy()
            expression = ['dummy']
            line_list = list(filter(None, line_list))
            for d, x in enumerate(line_list[1:-4]):
                if not re.match("[\d]+", x):
                    if x == "--undefined--":
                        nr_und += 1
                    else:
                        if not expression[-1] == x:
                            expression.append(x)

                            # store the mean values
                            ind = 0
                            for b in line_list[d+1:d+22]:
                                if b != line_list[d+1] and 'tot_dur' not in line_list[d+1:d+22]:
                                    if b != "--undefined--" and float(b) > 0:
                                        nr_means[ind] += 1
                                        means[ind] += float(b)
                                    ind += 1
                elif float(x) <= 0:
                    nr_und += 1

            for nr, item in enumerate(['dur_mean', 'pitch_min_mean', 'pitch_max_mean', 'pitch_mean_mean',
                                       'pitch_std_mean', 'pitch_var_mean', 'intensity_min_mean', 'intensity_max_mean',
                                       'intensity_mean_mean', 'intensity_std_mean', 'f0_mean', 'f1_mean', 'f2_mean',
                                       'f3_mean', 'grav_center_mean']):
                row_dict[item] = means[nr]/nr_means[nr]

            row_dict['expression'] = " ".join(expression[1:])
            row_dict['nr_undefined'] = nr_und

            # add the row back to the list
            dict_list[i] = row_dict
    return dict_list

    # de 66 de 171.91 184.76 178.68 5.33 de 798.78 de 54.55 70.65 67.13 6.19 de 372 1636 2791 4545 de 282
    # duration -> pitch min max mean std -> pitch variability -> intensity min max mean std -> formants -> center of gravity


def run():
    """
    Run the program to extract the relevant information from different text files and store in one excel file
    """

    # Create a new dataframe to store all information in
    data = create_dataframe()

    # Loop through all the result files in the current directory
    files_total = glob.glob("results_[a-z0-9]*.txt")
    for i, f in enumerate(files_total):

        # Extract the information from the corresponding files and store in the dataframe
        result = extract_from_results(f)
        for d in result:
            data = data.append(d, ignore_index=True)

        # Print the progress
        print("File " + str(i + 1) + " of " + str(len(files_total)) + " done")

    # Save the dataframe
    output = "extracted_info.xlsx"
    print(str(len(files_total)) + " files processed. Storing the extracted data into " + output)
    data.to_excel(output, index=False)


run()