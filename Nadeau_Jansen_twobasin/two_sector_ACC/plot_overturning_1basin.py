#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 15:32:58 2019

@author: malte
"""
from matplotlib import pyplot as plt
import numpy as np
from interp_channel import Interpolate_channel
from interp_twocol import Interpolate_twocol
from psi_thermwind import Psi_Thermwind
# parameters are (input filename, bbot, f, figure filename) 
case=('1basin_60.npz',-0.0011,1e-4,'1basin_60') 

#path where figures should be saved:
path='/Users/malte/Dropbox/column-2Basin/Figs-pymoc/kappa_tanh_final/'

bbot= case[1]

plt.close('all')

z=np.asarray(np.linspace(-4000, 0, 80))
y=np.asarray(np.linspace(0,3.e6, 51))

# Notice that this is just because I forgot to save it. Doesn't work
# if surface b-profile is changed!!!
offset=0.0345*(1-np.cos(np.pi*(5.55e5-1.e5)/8e6));
bs_SO=(0.0345*(1-np.cos(np.pi*(y-1.e5)/8e6))*(y>5.55e5)
      +(bbot-offset)/5.55e5*np.maximum(0,5.55e5-y)+offset*(y<5.55e5));



Psi_SO_Atl=1.0*np.load(case[0])['Psi_SO_Atl']
b_Atl=1.0*np.load(case[0])['b_Atl']
b_north=1.0*np.load(case[0])['b_north']

AMOC = Psi_Thermwind(z=z,b1=b_Atl,b2=b_north)
AMOC.solve()
AMOC.Psib() # needed to generate bgrid


blevs=np.array([-0.004,-0.002,0.0,0.004,0.01,0.018])
#np.concatenate((np.arange(-0.01,0.006,0.002),np.arange(0.006,0.04,0.004))) 
#plevs=np.arange(-20.,22,2.0)
plevs=np.arange(-21.,23.,2.0)
nb=500;

b_basin=b_Atl;
# Compute total SO residual overturning by first interpolating circulation 
# in both sectors to mean buoyancy profile values and then summing (at constant b).
PsiSO=Psi_SO_Atl;
AMOC_bbasin=np.interp(b_basin,AMOC.bgrid,AMOC.Psib());
# this is to Plot adiabatic overturning only:
PsiSO_bgrid=(np.interp(AMOC.bgrid,b_Atl,Psi_SO_Atl));
Psi_ad=np.maximum(np.minimum(AMOC.Psib(),PsiSO_bgrid),0.);
PsiSO_ad=np.interp(b_basin,AMOC.bgrid,Psi_ad);
Psi_north_ad=np.interp(b_north,AMOC.bgrid,Psi_ad);
AMOC_bbasin_ad=np.interp(b_basin,AMOC.bgrid,Psi_ad);

l=y[-1];

bs=1.*bs_SO;bn=1.*b_basin;
bs[-1]=1.*bn[-1]; # if bs is tiny bit warmer there is a zero slope point at the surface which makes the interpolation fail...

# first interpolate buoyancy in channel along constant-slope isopycnals: 
bint=Interpolate_channel(y=y,z=z,bs=bs,bn=bn)
bsouth=bint.gridit()
# buoyancy in the basin is all the same:
lbasin=11000.
ltrans=1500.
lnorth=400.
lchannel=l/1e3
ybasin=np.linspace(0,lbasin,60)+lchannel;
bbasin=np.tile(b_basin,(len(ybasin),1))
bAtl=np.tile(b_Atl,(len(ybasin),1))
# interpolate buoyancy in northern ransition region:
ytrans=np.linspace(ltrans/20.,ltrans,20)+lchannel+lbasin;
bn=b_north.copy();
bn[0]=b_basin[0];# Notice that the interpolation procedure assumes that the bottom
#buoyancies in both colums match - which may not be exactly the case depending
# on when in teh time-step data is saved 
bint=Interpolate_twocol(y=ytrans*1000.-ytrans[0]*1000.,z=z,bs=b_Atl,bn=bn)
btrans=bint.gridit()
# finally set buyancy in northern deep water formation region:
ynorth=np.linspace(lnorth/20.,lnorth,20)+lchannel+lbasin+ltrans;
bnorth=np.tile(bn,(len(ynorth),1))
# now stick it all together:
ynew=np.concatenate((y/1e3,ybasin,ytrans,ynorth))
bnew=np.concatenate((bsouth,bbasin,btrans,bnorth))
bnew_Atl=np.concatenate((np.nan*bsouth,bAtl,btrans,bnorth))

# Compute z-coordinate and residual overturning streamfunction at all latitudes:
psiarray_b=np.zeros((len(ynew),len(z))) # overturning in b-coordinates
psiarray_b_Atl=np.zeros((len(ynew),len(z))) # overturning in b-coordinates
psiarray_b_Atl_ad=np.zeros((len(ynew),len(z))) # overturning in b-coordinates
psiarray_res=np.zeros((len(ynew),len(z))) # "residual" overturning - i.e. isopycnal overturning mapped into z space
psiarray_Atl=np.zeros((len(ynew),len(z))) # "residual" overturning in ATl.
psiarray_z=np.zeros((len(ynew),len(z)))   # z-space, "eulerian" overturning
psiarray_z_Atl=np.zeros((len(ynew),len(z)))  # z-space, "eulerian" overturning
for iy in range(1,len(y)):
    # in the channel, interpolate PsiSO onto local isopycnal depth:
    psiarray_res[iy,:]=np.interp(bnew[iy,:],b_basin,PsiSO)
    psiarray_z[iy,:]=np.interp(bnew[iy,:],b_basin,Psi_SO_Atl)
    psiarray_z_Atl[iy,:]=psiarray_z[iy,:]
    psiarray_b[iy,b_basin<bs_SO[iy]]=PsiSO[b_basin<bs_SO[iy]]
    psiarray_Atl[iy,:]=psiarray_res[iy,:];    
    psiarray_b_Atl[iy,:]=psiarray_b[iy,:];    
for iy in range(len(y),len(y)+len(ybasin)):
    # in the basin, linearly interpolate between Psi_SO and Psi_AMOC:
    psiarray_res[iy,:]=((ynew[iy]-lchannel)*np.interp(b_basin,AMOC.bgrid,AMOC.Psib())+(lchannel+lbasin-ynew[iy])*PsiSO)/lbasin   
    psiarray_z[iy,:]=((ynew[iy]-lchannel)*AMOC.Psi+(lchannel+lbasin-ynew[iy])*(Psi_SO_Atl))/lbasin  
    psiarray_z_Atl[iy,:]=((ynew[iy]-lchannel)*AMOC.Psi+(lchannel+lbasin-ynew[iy])*(Psi_SO_Atl))/lbasin  
    psiarray_b[iy,:]=((ynew[iy]-lchannel)*AMOC_bbasin
                      +(lchannel+lbasin-ynew[iy])*PsiSO)/lbasin  
    psiarray_Atl[iy,:]=((ynew[iy]-lchannel)*AMOC.Psibz()[0]+(lchannel+lbasin-ynew[iy])*(Psi_SO_Atl))/lbasin   
    psiarray_b_Atl[iy,:]=((ynew[iy]-lchannel)*AMOC_bbasin+
                    (lchannel+lbasin-ynew[iy])*np.interp(b_basin,b_Atl,Psi_SO_Atl))/lbasin   
for iy in range(len(y)+len(ybasin),len(y)+len(ybasin)+len(ytrans)):
    # in the northern transition region, interpolate AMOC.psib to local isopycnal depth
    # for psi_res, while keeping psi_z constant and psi_z constant on non-outcropped isopycnals:
    psiarray_res[iy,:]=np.interp(bnew[iy,:],AMOC.bgrid,AMOC.Psib())
    psiarray_z[iy,:]=AMOC.Psi      
    psiarray_z_Atl[iy,:]=AMOC.Psi      
    #psiarray_z[iy,:]=((lchannel+lbasin+lnorth-ynew[iy])*AMOC.Psi)/lnorth      
    psiarray_b[iy,b_basin<bnew[iy,-1]]=AMOC_bbasin[b_basin<bnew[iy,-1]]      
    psiarray_Atl[iy,:]=np.interp(bnew[iy,:],AMOC.bgrid,AMOC.Psib())
    psiarray_b_Atl[iy,b_basin<bnew[iy,-1]]=psiarray_b[iy,b_basin<bnew[iy,-1]]
for iy in range(len(y)+len(ybasin)+len(ytrans),len(ynew)):
    # in the northern sinking region, all psi decrease linearly to zero:
    psiarray_res[iy,:]=((lchannel+lbasin+ltrans+lnorth-ynew[iy])*AMOC.Psibz(nb=nb)[1])/lnorth
    psiarray_z[iy,:]=((lchannel+lbasin+ltrans+lnorth-ynew[iy])*AMOC.Psi)/lnorth      
    psiarray_z_Atl[iy,:]=((lchannel+lbasin+ltrans+lnorth-ynew[iy])*AMOC.Psi)/lnorth      
    psiarray_b[iy,b_basin<bnew[iy,-1]]=((lchannel+lbasin+ltrans+lnorth-ynew[iy])
        *AMOC_bbasin[b_basin<bnew[iy,-1]])/lnorth      
    psiarray_Atl[iy,:]=((lchannel+lbasin+ltrans+lnorth-ynew[iy])*AMOC.Psibz(nb=nb)[1])/lnorth
    psiarray_b_Atl[iy,b_basin<bnew[iy,-1]]=psiarray_b[iy,b_basin<bnew[iy,-1]]
#psiarray_res[-1,:]=0.;

# plot z-coordinate overturning and buoyancy structure:
fig = plt.figure(figsize=(10.8,6.8))
ax1 =fig.add_axes([0.1,.57,.33,.36])
ax2 = ax1.twiny()
plt.ylim((-4e3,0))
ax1.set_ylabel('Depth [m]', fontsize=13)
ax1.set_xlim((-20,30))
ax2.set_xlim((-0.02,0.030))
ax1.set_xlabel('$\Psi$ [SV]', fontsize=13)
ax2.set_xlabel('$b_B$ [m s$^{-2}$]', fontsize=13)
ax1.plot(AMOC.Psi, AMOC.z,'--r', linewidth=1.5)
ax1.plot(Psi_SO_Atl, z, '--b', linewidth=1.5)
ax2.plot(b_Atl, z, '-b', linewidth=1.5)
ax2.plot(b_north, z, '-r', linewidth=1.5)     
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc=4, frameon=False)
ax1.plot(0.*z, z,linewidth=0.5,color='k',linestyle=':')

ax1 = fig.add_subplot(222)
CS=ax1.contour(ynew,z,bnew.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,psiarray_z.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_z.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Global',fontsize=12)
       
ax1 = fig.add_subplot(223)
CS=ax1.contour(ynew,z,0.*bnew_Atl.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,0.*psiarray_z_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,0.*psiarray_z_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Pacific',fontsize=12)
ax1.invert_xaxis()


ax1 = fig.add_subplot(224)
CS=ax1.contour(ynew,z,bnew_Atl.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,psiarray_z_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_z_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
#ax1.tick_params(labelleft=False) 
#ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Atlantic',fontsize=12)

fig.tight_layout()   
fig.subplots_adjust(right=0.93)
cbar_ax = fig.add_axes([0.945, 0.1, 0.012, 0.8])
fig.colorbar(CS, cax=cbar_ax,ticks=np.arange(-20,21,5), orientation='vertical')

plt.savefig(path+case[3]+'_z.png', format='png', dpi=400)

# plot global residual overturning and global mean buoyancy structure:
        
#fig = plt.figure(figsize=(10,7.5))
fig = plt.figure(figsize=(10.8,6.8))

# Notice that this isn't all really "residual", but it's also not clear
# which buoyancy to interpolate residual overturning between two columns to
ax1 =fig.add_axes([0.1,.57,.33,.36])
ax2 = ax1.twiny()
plt.ylim((-4e3,0))
ax1.set_ylabel('Depth [m]', fontsize=13)
ax1.set_xlim((-20,30))
ax2.set_xlim((-0.02,0.030))
ax1.set_xlabel('$\Psi$ [SV]', fontsize=13)
ax2.set_xlabel('$b_B$ [m s$^{-2}$]', fontsize=13)
ax1.plot(AMOC.Psi, AMOC.z,'--r', linewidth=1.5)
#ax1.plot(Psi_SO_Atl, SO_Atl.z, ':b', linewidth=1.5)
ax1.plot(Psi_SO_Atl, z, '--b', linewidth=1.5)
ax1.plot(PsiSO, z, '--k', linewidth=1.5)
ax2.plot(b_Atl, z, '-b', linewidth=1.5)
ax2.plot(b_north, z, '-r', linewidth=1.5)     
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc=4, frameon=False)
ax1.plot(0.*z, z,linewidth=0.5,color='k',linestyle=':')

ax1 = fig.add_subplot(222)
CS=ax1.contour(ynew,z,bnew.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,psiarray_res.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_res.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Global',fontsize=12)
       
ax1 = fig.add_subplot(223)
CS=ax1.contour(ynew,z,0.*bnew_Atl.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,0.*psiarray_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,0.*psiarray_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Pacific',fontsize=12)
ax1.invert_xaxis()

ax1 = fig.add_subplot(224)
CS=ax1.contour(ynew,z,bnew_Atl.transpose()/2e-3,levels=blevs/2e-3,colors='k',linewidths=1.0,linestyles='solid')
ax1.clabel(CS,fontsize=10,fmt='%1.0f')
ax1.contour(ynew,z,psiarray_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
#ax1.set_ylabel('Depth [m]',fontsize=12)
ax1.set_title('Atlantic',fontsize=12)

fig.tight_layout()   
fig.subplots_adjust(right=0.93)
cbar_ax = fig.add_axes([0.945, 0.1, 0.012, 0.83])
fig.colorbar(CS, cax=cbar_ax,ticks=np.arange(-20,21,5), orientation='vertical')

plt.savefig(path+case[3]+'_res.png', format='png', dpi=400)


# Plot Isopycnal overturning

fig = plt.figure(figsize=(10.8,6.8))
ax1 =fig.add_axes([0.1,.57,.33,.36])
ax2 = ax1.twiny()
plt.ylim((-4e3,0))
ax1.set_ylabel('b [m s$^{-2}$]', fontsize=13)
ax1.set_xlim((-20,30))
ax2.set_xlim((-0.02,0.030))
ax1.set_xlabel('$\Psi$ [SV]', fontsize=13)
ax2.set_xlabel('$b_B$ [m s$^{-2}$]', fontsize=13)
ax1.plot(AMOC_bbasin, z,'--r', linewidth=1.5)
ax1.plot(np.interp(b_basin,b_Atl,Psi_SO_Atl), z, '--b', linewidth=1.5)
ax1.plot(PsiSO, z, '--k', linewidth=1.5)
ax2.plot(b_Atl, z, '-b', linewidth=1.5)
ax2.plot(b_north, z, '-r', linewidth=1.5)     
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc=4, frameon=False)
ax1.plot(0.*b_basin, b_basin,linewidth=0.5,color='k',linestyle=':')
ax1.set_yticks(np.interp([0.02, 0.005,0.002,0.001,0.0005, 0.,-0.0005, -0.001 ],b_basin,z))
ax1.set_yticklabels([0.02, 0.005,0.002, 0.001,0.0005, 0.,-0.0005, -0.001 ])

ax1 = fig.add_subplot(222)
ax1.contour(ynew,z,psiarray_b.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_b.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('b [m s$^{-2}$]',fontsize=12)
ax1.set_title('Global',fontsize=12)
ax1.set_yticks(np.interp([0.02, 0.005,0.002,0.001,0.0005, 0.,-0.0005, -0.001 ],b_basin,z))
ax1.set_yticklabels([0.02, 0.005,0.002, 0.001,0.0005, 0.,-0.0005, -0.001 ])
#fig.colorbar(CS, ticks=plevs[0::5], orientation='vertical')
   
ax1 = fig.add_subplot(223)
ax1.contour(ynew,z,0.*psiarray_b_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,0.*psiarray_b_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
#ax1.plot(np.array([y[-1]/1000.,y[-1]/1000.]),np.array([-4000.,0.]),color='k')
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
ax1.set_ylabel('b [m s$^{-2}$]',fontsize=12)
ax1.set_title('Pacific',fontsize=12)
ax1.invert_xaxis()

ax1 = fig.add_subplot(224)
ax1.contour(ynew,z,psiarray_b_Atl.transpose(),levels=plevs,colors='k',linewidths=0.5)
CS=ax1.contourf(ynew,z,psiarray_b_Atl.transpose(),levels=plevs,cmap=plt.cm.bwr, vmin=-20, vmax=20)
ax1.plot(np.array([y[-1]/1000.,y[-1]/1000.]),np.array([-4000.,0.]),color='k')
ax1.set_xlim([0,ynew[-1]])
ax1.set_xlabel('y [km]',fontsize=12)
#ax1.set_ylabel('b [m s$^{-2}$]',fontsize=12)
ax1.set_title('Atlantic',fontsize=12)
ax1.set_yticks(np.interp([0.02, 0.005,0.002,0.001,0.0005, 0.,-0.0005, -0.001 ],b_basin,z))
ax1.set_yticklabels([0.02, 0.005,0.002, 0.001,0.0005, 0.,-0.0005, -0.001 ])

fig.tight_layout()   
fig.subplots_adjust(right=0.93)
cbar_ax = fig.add_axes([0.945, 0.1, 0.012, 0.8])
fig.colorbar(CS, cax=cbar_ax,ticks=np.arange(-20,21,5), orientation='vertical')

plt.savefig(path+case[3]+'_b.png', format='png', dpi=400)

