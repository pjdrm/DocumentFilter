import matplotlib.pyplot as plt
import numpy as np

alpha = [100, 90, 1]
dir = np.random.dirichlet(alpha)
dirs = [alpha, dir]
n = 10
for i in range(n):
    dirs.append(np.random.dirichlet(dir))
    
f, ax= plt.subplots(n+2, 1, figsize=(16, 16), sharex=True)
for i, dir in enumerate(dirs):
    ax[i].stem(dir, linefmt='r-', markerfmt='ro', basefmt='w-')
    ax[i].set_xlim(-1, 3)
    ax[i].set_ylim(0, 1)
    ax[i].set_ylabel("Prob")
    if i == 0:
        ax[i].set_title("Alpha")
    elif i == 1:
        ax[i].set_title("Document Dirichlet".format(i))
    else:
        ax[i].set_title("Segment Dirichlet {}".format(i-2))

ax[1].set_xlabel("Topic")

plt.tight_layout()
plt.show()

'''
fig = plt.figure(figsize=(4,3))
ax = fig.add_subplot(1,1,1)
ax.stem([1,2,3], dir2)
ax.set_xticks([0,1,2,3,4])
ax.set_yticks([0, 1.5])
plt.show()
'''