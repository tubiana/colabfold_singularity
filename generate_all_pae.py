import os
import matplotlib.pyplot as plt 
import json
from glob import glob
import pandas as pd
import argparse


#FOnction that call argparse with arguments :
# path : path to the directory containing the predictions
# outputgraph : path to the output graph
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a mega plot of all PAE matrices from AlphaFold2 predictions")
    parser.add_argument("--Folder", "-f", help="Path to the directory containing the predictions", required=True)
    parser.add_argument("--server","-s", help="Data geenrated from I2BC AF server ?", default=True)
    return parser.parse_args()


def generate_mega_PAE(path, server=True,):

    if server==True:
        workingpath = path+"/predictions" 
        outputgraph = "./plots/all_PAE.png"
        jsonsglob  = './scores/*seed*.json'
    else:
        workingpath = path
        outputgraph = "all_PAE.png"
        jsonsglob = "*seed*.json"

    os.chdir(workingpath)
    curdir = os.getcwd()

    models = [f for f in os.listdir() if os.path.isdir(f)]
    if server != True:
        #clean "_env" and "_pairgreedy"  for each model and keep only unique names
        models = list(set([model.split("_env")[0] for model in models]))
        models = list(set([model.split("_pairgreedy")[0] for model in models]))


    for model in models:        
        if server == True or len(models) > 1:
            os.chdir(model)
        #find recurcively all json files in the format *seed*.json
        json_files = glob(jsonsglob, recursive=True)

        # Initialize variables for the subplot layout
        num_files = len(json_files)
        num_cols = 5
        num_rows = (num_files // num_cols) + (num_files % num_cols > 0)

        #Get the data sorted
        df = pd.DataFrame(json_files, columns=["file"])
        df["seed"] = df["file"].str.extract(r"seed_(\d+)")
        df["rank_global"] = df["file"].str.extract(r"rank_(\d+)")

        #group by seed and in each group rank by rank_global and create a new "rank" column with values between 1 and number of members in the group
        df["rank"] = df.groupby("seed")["rank_global"].rank(method="first", ascending=True).astype(int)
        df = df.sort_values(by=["seed","rank"])
        json_files_sorted = df["file"].tolist()

        #extract the first line of A3M and parse it, example : 
        # #144,1051    2,1 means to have [144,144,1051]
        with open(model+".a3m") as f:
            firstline = f.readline()
            split = firstline.strip().replace("#","").split("\t")
            sequence_length = split[0].split(",")
            repetitions = split[1].split(",")

            bar_position = []
            previous = 0
            totalsize=0
            for i in range(len(sequence_length)):
                for j in range(int(repetitions[i])):
                    bar_position.append(previous)
                    previous = previous+int(sequence_length[i])
                    totalsize = totalsize + int(sequence_length[i])
            bar_position.append(totalsize)


        tick = [int((bar_position[i-1]+bar_position[i])/2) for i in range(1,len(bar_position))]
        tick_label = [chr(i) for i in range(65,65+len(tick))]
        bar_position=bar_position[1:-1]
                    

        # Create a figure and subplots
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(16, 3*num_rows))

        # Iterate over df rows 
        for i in range(len(df)):
            file = df.iloc[i,]["file"] 
            # Load the JSON data
            with open(file) as f:
                data = json.load(f)
            
            seed = df.iloc[i,]["seed"]
            rank = df.iloc[i,]["rank"]
            rank_global = df.iloc[i,]["rank_global"]
            # Extract the alphafold PAE matrix
            pae_matrix = data['pae']
            
            # Determine the subplot position
            row = i // num_cols
            col = i % num_cols          
            
            # Plot the PAE matrix
            axs[row, col].imshow(pae_matrix, cmap='bwr', interpolation='nearest', vmin=0, vmax=30)

            for j in range(len(bar_position)):
                axs[row, col].axvline(x=bar_position[j], color='black', linewidth=1.5)
                axs[row, col].axhline(y=bar_position[j], color='black', linewidth=1.5)

            # axis tick labels from tick and tick_labels
            axs[row, col].yaxis.set_ticks(tick)
            axs[row, col].yaxis.set_ticklabels(tick_label)

                       
            axs[row, col].set_title(f"seed {seed} rank {rank} (G:{rank_global})", fontsize=10)



        # Finally, make a unique legend for all subplots, values are from 0 to 30.
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
        cbar_ax.set_title('PAE')
        fig.colorbar(plt.imshow(pae_matrix, cmap='bwr', interpolation='nearest', vmin=0, vmax=30), cax=cbar_ax)
        # Adjust the layout and display the plot
        #plt.tight_layout()
        plt.savefig(outputgraph, dpi=300)

        #Come back to previous directory to change mode (if any)
        os.chdir(curdir)
        return df


#Now the main : 
if __name__ == "__main__":
    args = parse_args()
    folder = args.Folder
    #get absolute path of "folder"
    folder = os.path.abspath(folder)
    server = args.server
    generate_mega_PAE(folder, server)
    print(f"Output graph saved in plots/all_PAE.png")