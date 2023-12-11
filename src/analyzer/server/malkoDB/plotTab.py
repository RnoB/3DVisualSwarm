




def plotTab(plot):
    filename = 'mov_xy.gif'
    tab = 4


    if int(plot) == 1:
        filename = 'mov_rz.gif'
        tab = 2
    if int(plot) == 2:
        filename = 'mov_xfv.gif'
    if int(plot) == 3:
        filename = 'stereo.gif'
        tab = 1

    if int(plot) == 4:
        filename = 'full_xy.png'
    if int(plot) == 5:
        filename = 'full_rz.png'
        tab = 2
    if int(plot) == 6:
        filename = 'full_xfv.png'


    if int(plot) == 7:
        filename = 'hist_x_r.png'
    if int(plot) == 8:
        filename = 'hist_x_phi.png'
    if int(plot) == 9:
        filename = 'hist_x_z.png'


    if int(plot) == 10:
        filename = 'plot_x_r.png'
        tab = 1
    if int(plot) == 11:
        filename = 'plot_x_phi.png'
        tab = 1
    if int(plot) == 12:
        filename = 'plot_x_z.png'
        tab = 1



    if int(plot) == 13:
        filename = 'hist_v_r.png'
    if int(plot) == 14:
        filename = 'hist_v_phi.png'
    if int(plot) == 15:
        filename = 'hist_v_z.png'


    if int(plot) == 16:
        filename = 'plot_v_r.png'
        tab = 1
    if int(plot) == 17:
        filename = 'plot_v_phi.png'
        tab = 1
    if int(plot) == 18:
        filename = 'plot_v_z.png'
        tab = 1

    if int(plot) == 19:
        filename = 'hist_a_r.png'
    if int(plot) == 20:
        filename = 'hist_a_phi.png'
    if int(plot) == 21:
        filename = 'hist_a_z.png'


    if int(plot) == 22:
        filename = 'plot_a_r.png'
        tab = 1
    if int(plot) == 23:
        filename = 'plot_a_phi.png'
        tab = 1
    if int(plot) == 24:
        filename = 'plot_a_z.png'
        tab = 1


    if int(plot) == 25:
        filename = 'hist_xvf_r.png'
    if int(plot) == 26:
        filename = 'hist_xvf_phi.png'
    if int(plot) == 27:
        filename = 'hist_xvf_z.png'


    if int(plot) == 28:
        filename = 'plot_xvf_r.png'
        tab = 1
    if int(plot) == 29:
        filename = 'plot_xvf_phi.png'
        tab = 1
    if int(plot) == 30:
        filename = 'plot_xvf_z.png'
        tab = 1


    if int(plot) == 31:
        filename = 'katz_dens.png'
    if int(plot) == 32:
        filename = 'katz_v.png'
    if int(plot) == 33:
        filename = 'katz_phi.png'

    if int(plot) == 34:
        filename = 'katz_dens_fishVR1.png'
    if int(plot) == 35:
        filename = 'katz_v_fishVR1.png'
    if int(plot) == 36:
        filename = 'katz_phi_fishVR1.png'
    if int(plot) == 37:
        filename = 'katz_dens_fishVR2.png'
    if int(plot) == 38:
        filename = 'katz_v_fishVR2.png'
    if int(plot) == 39:
        filename = 'katz_phi_fishVR2.png'
    if int(plot) == 40:
        filename = 'katz_dens_fishVR3.png'
    if int(plot) == 41:
        filename = 'katz_v_fishVR3.png'
    if int(plot) == 42:
        filename = 'katz_phi_fishVR3.png'
    if int(plot) == 43:
        filename = 'katz_dens_fishVR4.png'
    if int(plot) == 44:
        filename = 'katz_v_fishVR4.png'
    if int(plot) == 45:
        filename = 'katz_phi_fishVR4.png'
    if int(plot) == 46:
        filename = 'katz_dens_fishVR5.png'
    if int(plot) == 47:
        filename = 'katz_v_fishVR5.png'
    if int(plot) == 48:
        filename = 'katz_phi_fishVR5.png'


    if int(plot) == 49:
        filename = 'vavg.png'
        tab = 3
    if int(plot) == 50:
        filename = 'Dvavg.png'
        tab = 3
    if int(plot) == 51:
        filename = 'Dpavg.png'
        tab = 3

    if int(plot) == 52:
        filename = 'vavg_FishVR1.png'
        tab = 3
    if int(plot) == 53:
        filename = 'Dvavg_FishVR1.png'
        tab = 3
    if int(plot) == 54:
        filename = 'Dpavg_FishVR1.png'
        tab = 3
    if int(plot) == 55:
        filename = 'vavg_FishVR2.png'
        tab = 3
    if int(plot) == 56:
        filename = 'Dvavg_FishVR2.png'
        tab = 3
    if int(plot) == 57:
        filename = 'Dpavg_FishVR2.png'
        tab = 3
    if int(plot) == 58:
        filename = 'vavg_FishVR3.png'
        tab = 3
    if int(plot) == 59:
        filename = 'Dvavg_FishVR3.png'
        tab = 3
    if int(plot) == 60:
        filename = 'Dpavg_FishVR3.png'
        tab = 3
    if int(plot) == 61:
        filename = 'vavg_FishVR4.png'
        tab = 3
    if int(plot) == 62:
        filename = 'Dvavg_FishVR4.png'
        tab = 3
    if int(plot) == 63:
        filename = 'Dpavg_FishVR4.png'
        tab = 3
    if int(plot) == 64:
        filename = 'vavg_FishVR5.png'
        tab = 3
    if int(plot) == 65:
        filename = 'Dvavg_FishVR5.png'
        tab = 3
    if int(plot) == 66:
        filename = 'Dpavg_FishVR5.png'
        tab = 3





    return filename,tab