'''
This script shows an example of how to use the model_PsiNA class   
'''

from model_PsiNA import Model_PsiNA
import numpy as np
from matplotlib import pyplot as plt

# buoyancy profile in the basin
# We will here assume b_N=0 (the default)
def b_basin(z): return 0.03*np.exp(z/300.)-0.0004

z=np.asarray(np.linspace(-4000, 0, 100))

# the next line would turn b_basin from a function to an array,
# which is also a valid input to Model_PsiNA 
#b_basin=b_basin(z)

# create column model instance
m = Model_PsiNA(z=z,b_basin=b_basin)
# solve the model:
m.solve()
    
# Plot results:
fig = plt.figure(figsize=(6,10))
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
ax1.plot(m.Psi_N, m.z)
ax2.plot(m.b_N, m.z)
ax2.plot(m.b_basin, m.z)
plt.ylim((-4e3,0))
ax1.set_xlim((-5,20))
ax2.set_xlim((-0.01,0.04))
