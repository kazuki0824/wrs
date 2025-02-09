import numpy as np
import math
import basis.robot_math as rm
import visualization.panda.world as wd
import robot_sim.robots.yumi.yumi as ym
import modeling.geometric_model as gm
import motion.optimization_based.incremental_nik as inik
import matplotlib.pyplot as plt

if __name__ == "__main__":
    base = wd.World(cam_pos=[3, -1, 1], lookat_pos=[0, 0, 0.5])
    gm.gen_frame(length=.2).attach_to(base)
    yumi_s = ym.Yumi(enable_cc=True)
    inik_svlr = inik.IncrementalNIK(yumi_s)
    component_name = 'rgt_arm'
    circle_center_pos = np.array([.5, -.4, .4])
    circle_ax = rm.rotmat_from_axangle(np.array([0,1,0]), -math.pi/3).dot(np.array([1,0,0]))
    radius = .17
    start_rotmat = rm.rotmat_from_axangle([0, 1, 0], math.pi / 2)
    end_rotmat = rm.rotmat_from_axangle(np.array([0,0,1]), -math.pi/3)
    jnt_values_list, tcp_list = inik_svlr.gen_circular_motion(component_name,
                                                    circle_center_pos,
                                                    circle_ax,
                                                    start_rotmat,
                                                    end_rotmat,
                                                    granularity=.3,
                                                    radius=radius,
                                                    toggle_tcp_list=True)
    print(jnt_values_list)
    import motion.trajectory.polynomial as trajp
    control_frequency = .005
    interval_time = 1
    traj_gen = trajp.TrajPoly(method="quintic")
    interpolated_confs, interpolated_spds, interpolated_accs = \
        traj_gen.piecewise_interpolation(jnt_values_list, control_frequency=control_frequency, interval_time=interval_time)

    fig, axs = plt.subplots(3, figsize=(3.5,4.75))
    fig.tight_layout(pad=.7)
    x = np.linspace(0, interval_time*(len(jnt_values_list) - 1), (len(jnt_values_list) - 1) * math.floor(interval_time / control_frequency))
    axs[0].plot(x, interpolated_confs)
    axs[0].plot(range(0, interval_time * (len(jnt_values_list)), interval_time), jnt_values_list, '--o')
    axs[1].plot(x, interpolated_spds)
    axs[2].plot(x, interpolated_accs)
    plt.show()
    for i in range(len(tcp_list)-1):
        spos = tcp_list[i][0]
        srotmat = tcp_list[i][1]
        epos = tcp_list[i+1][0]
        erotmat = tcp_list[i+1][1]
        print(spos, epos)
        gm.gen_dasharrow(spos, epos, thickness=.01, rgba=[1,0,0,1]).attach_to(base)
        gm.gen_mycframe(epos, erotmat, alpha=.7).attach_to(base)
    yumi_s.fk(component_name, jnt_values_list[1])
    yumi_s.gen_meshmodel(toggle_tcpcs=False, rgba=[.7,.3,.3,.57]).attach_to(base)
    yumi_s.fk(component_name, jnt_values_list[2])
    yumi_s.gen_meshmodel(toggle_tcpcs=False, rgba=[.3,.7,.3,.57]).attach_to(base)
    yumi_s.fk(component_name, jnt_values_list[3])
    yumi_s.gen_meshmodel(toggle_tcpcs=False, rgba=[.3,.3,.7,.57]).attach_to(base)
    yumi_s.fk(component_name, jnt_values_list[0])
    yumi_s.gen_meshmodel(toggle_tcpcs=True).attach_to(base)
    # base.run()
    x = np.arange(len(jnt_values_list))
    print(x)
    plt.figure(figsize=(3,5))
    plt.plot(x, jnt_values_list, '-o')
    plt.xticks(x)
    plt.show()
    base.run()