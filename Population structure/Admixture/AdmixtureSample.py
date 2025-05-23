import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

## Loading PCA results
with open(EigenValueFile) as fin:
    EigenValue=[z.strip() for z in fin]
    EigenDict=dict(('PC'+str(u+1),float(v)) for u,v in enumerate(EigenValue))

usecols=['IID']+['PC{}_AVG'.format(z) for z in range(1, 11)]
RenameDict=dict(('PC{}_AVG'.format(z),'PC{}'.format(z)) for z in range(1, 11))
PCsDF=pd.read_csv(ScoreFile,sep='\t',usecols=usecols)
PCsDF.rename(columns=RenameDict,inplace=True)
for item in ['PC'+str(z) for z in range(1,11)]:
    PCsDF[item]=PCsDF[item]/(-np.sqrt(EigenDict.get(item))/2)

## Population Density-Based Division
## - PC1 and PC2 percentile thresholds (2% and 98%)
## - Nine-block stratification for balanced representation
BoundaryPercentile=2 
Xaxis='PC1'
Yaxis='PC2'
Xaxis_lower=round(np.percentile(PCsDF[Xaxis],BoundaryPercentile),4)
Xaxis_upper=round(np.percentile(PCsDF[Xaxis],100-BoundaryPercentile),4)
Xaxis_min=PCsDF[Xaxis].min()
Xaxis_max=PCsDF[Xaxis].max()

Yaxis_lower=round(np.percentile(PCsDF[Yaxis],BoundaryPercentile),4)
Yaxis_upper=round(np.percentile(PCsDF[Yaxis],100-BoundaryPercentile),4)
Yaxis_min=PCsDF[Yaxis].min()
Yaxis_max=PCsDF[Yaxis].max()

print(f"Lower bound of {Xaxis} : {Xaxis_lower}")
print(f"Upper bound of {Xaxis} : {Xaxis_upper}")
print(f"Lower bound of {Yaxis} : {Yaxis_lower}")
print(f"Upper bound of {Yaxis} : {Yaxis_upper}")

A=PCsDF[(PCsDF[Xaxis]<=Xaxis_lower) & (PCsDF[Yaxis]<=Yaxis_lower)]
B=PCsDF[(PCsDF[Xaxis]>Xaxis_lower) & (PCsDF[Xaxis]<=Xaxis_upper) & (PCsDF[Yaxis]<=Yaxis_lower)]
C=PCsDF[(PCsDF[Xaxis]>Xaxis_upper) & (PCsDF[Yaxis]<=Yaxis_lower)]

D=PCsDF[(PCsDF[Xaxis]<=Xaxis_lower) & (PCsDF[Yaxis]>Yaxis_lower) & (PCsDF[Yaxis]<=Yaxis_upper)]
E=PCsDF[(PCsDF[Xaxis]>Xaxis_lower) & (PCsDF[Xaxis]<=Xaxis_upper) & (PCsDF[Yaxis]>Yaxis_lower) & (PCsDF[Yaxis]<=Yaxis_upper)]
F=PCsDF[(PCsDF[Xaxis]>Xaxis_upper) & (PCsDF[Yaxis]>Yaxis_lower) & (PCsDF[Yaxis]<=Yaxis_upper)]

G=PCsDF[(PCsDF[Xaxis]<=Xaxis_lower) & (PCsDF[Yaxis]>Yaxis_upper)]
H=PCsDF[(PCsDF[Xaxis]>Xaxis_lower) & (PCsDF[Xaxis]<=Xaxis_upper) & (PCsDF[Yaxis]>Yaxis_upper)]
I=PCsDF[(PCsDF[Xaxis]>Xaxis_upper) & (PCsDF[Yaxis]>Yaxis_upper)]

## Distribution of Samples Across Nine Blocks in PCA Space
savefigfile="CutForRefSample.png"
N_Block=pd.DataFrame()
ColorDef={'A':'deepskyblue','B':'darkgoldenrod','C':'yellow',
          'D':'seagreen','E':'blue','F':'coral',
          'G':'fuchsia','H':'deepskyblue','I':'red'}
Kwargs = { 'marker': '.', 'linewidth': 0, 's': 30, 'alpha': 1 }

fig, ax = plt.subplots(figsize=(10, 8))
for block, color in ColorDef.items(): 
    N_Block.loc[block,'N']=eval(block).shape[0]
    sns.scatterplot(data=eval(block), x=Xaxis, y=Yaxis, label=block, color=color, ax=ax, **Kwargs)
ax.hlines(y=Yaxis_lower, xmin=Xaxis_min, xmax=Xaxis_max, color='black',linestyle='--')
ax.hlines(y=Yaxis_upper, xmin=Xaxis_min, xmax=Xaxis_max, color='black',linestyle='--')
ax.vlines(x=Xaxis_lower, ymin=Yaxis_min, ymax=Yaxis_max, color='black',linestyle='--')
ax.vlines(x=Xaxis_upper, ymin=Yaxis_min, ymax=Yaxis_max, color='black',linestyle='--')

plt.legend(fontsize=20)
plt.xticks(fontsize=16) 
plt.yticks(fontsize=16)
plt.gca().set_xlabel(Xaxis, fontsize=18)
plt.gca().set_ylabel(Yaxis, fontsize=18)

handles, labels = ax.get_legend_handles_labels() 
ax.legend(handles, labels, prop={'size': 14}, markerscale=3)

plt.savefig(savefigfile,dpi=300,facecolor='white')


## Reference Samples
RefSample = [] 
for df in [B, D, F, G, H, I]: 
    RefSample.extend(df['IID'].tolist())  
E_sample = E.sample(n=round(E.shape[0]*0.01), random_state=1) 
RefSample.extend(E_sample['IID'].tolist())

## Visualization
savefigfile='RefSample.png'
RefDF=PCsDF[PCsDF['IID'].isin(RefSample)]

plt.figure(figsize=(10,8))
ax=sns.scatterplot(data=PCsDF,x=Xaxis,y=Yaxis,color='grey',markers='.',linewidth=0,s=10,label='TPMI')
sns.scatterplot(data=RefDF,x=Xaxis,y=Yaxis,color='red',markers='.',linewidth=0,s=10,label='Reference sample',alpha=1,ax=ax)

ax.hlines(y=Yaxis_lower, xmin=Xaxis_min, xmax=Xaxis_max, color='black',linestyle='--')
ax.hlines(y=Yaxis_upper, xmin=Xaxis_min, xmax=Xaxis_max, color='black',linestyle='--')
ax.vlines(x=Xaxis_lower, ymin=Yaxis_min, ymax=Yaxis_max, color='black',linestyle='--')
ax.vlines(x=Xaxis_upper, ymin=Yaxis_min, ymax=Yaxis_max, color='black',linestyle='--')

plt.legend(fontsize=18)
plt.xticks(fontsize=16) 
plt.yticks(fontsize=16)
plt.gca().set_xlabel(Xaxis, fontsize=18)
plt.gca().set_ylabel(Yaxis, fontsize=18)
handles, labels = ax.get_legend_handles_labels() 
ax.legend(handles, labels, prop={'size': 14}, markerscale=3)
plt.savefig(savefigfile,facecolor='white',dpi=300)



