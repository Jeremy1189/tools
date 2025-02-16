import os

# 设置环境变量
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from ase.io import read, write
from ase.neighborlist import primitive_neighbor_list, natural_cutoffs, find_mic
import numpy as np
import shutil


def generate_poscars_with_vacancies_and_neb(poscar_file):
    print("方法: 生成含单个空位的POSCAR文件并创建运行目录")

    # 创建存储生成的POSCAR文件的目录
    single_vac_dir = 'single_vac'
    if not os.path.exists(single_vac_dir):
        os.makedirs(single_vac_dir)

    # 读取POSCAR文件
    atoms = read(poscar_file)
    symbols = atoms.get_chemical_symbols()

    # 查找唯一元素及其索引
    element_indices = {}
    for i, symbol in enumerate(symbols):
        if symbol not in element_indices:
            element_indices[symbol] = []
        element_indices[symbol].append(i)

    # 遍历每个元素及其索引
    for element, indices in element_indices.items():
        for idx in indices:
            # 创建原子对象的副本
            new_atoms = atoms.copy()

            # 获取将被移除的原子的位置
            position = new_atoms[idx].position

            # 移除原子
            del new_atoms[idx]

            # 更新POSCAR头部的原子数量
            new_symbols = new_atoms.get_chemical_symbols()
            element_counts = {el: new_symbols.count(el) for el in set(new_symbols)}

            # 生成新的POSCAR文件名
            new_poscar_file = os.path.join(single_vac_dir, f"POSCAR_{element}_{idx}")

            # 写入新的POSCAR文件
            write(new_poscar_file, new_atoms, format='vasp')
            print(f"Generated {new_poscar_file} with {element} vacancy at index {idx} (position: {position})")

            # 生成run_ini_end目录
            run_ini_end_base_dir = 'run_ini_end'
            if not os.path.exists(run_ini_end_base_dir):
                os.makedirs(run_ini_end_base_dir)

            # 复制必要的VASP文件
            vasp_files_dir = './'  # 替换为你的VASP文件目录路径

            # 创建对应的运行目录
            run_ini_end_dir = os.path.join(run_ini_end_base_dir, f"run_ini_end_{idx}")
            if not os.path.exists(run_ini_end_dir):
                os.makedirs(run_ini_end_dir)

            # 复制初态POSCAR文件到run_ini_end子目录
            dst_poscar_path = os.path.join(run_ini_end_dir, 'POSCAR_ini')
            shutil.copy(new_poscar_file, dst_poscar_path)
            #创建初态计算目录
            run_ini_dir = os.path.join(run_ini_end_dir, f"run_ini")
            if not os.path.exists(run_ini_dir):
                os.makedirs(run_ini_dir)
            run_ini_poscar_path = os.path.join(run_ini_dir, 'POSCAR')    
            shutil.copy(new_poscar_file, run_ini_poscar_path)

            # 复制INCAR, POTCAR, KPOINTS文件到run_ini_end子目录
            #for file_name in ['INCAR', 'POTCAR', 'KPOINTS']:
            for file_name in ['INCAR', 'POTCAR']:
                src_file_path = os.path.join(vasp_files_dir, file_name)
                dst_file_path = os.path.join(run_ini_end_dir, file_name)
                shutil.copy(src_file_path, dst_file_path)
                run_ini_file_path = os.path.join(run_ini_dir, file_name)        
                shutil.copy(src_file_path, run_ini_file_path)
            # 创建NEB计算的初态和末态目录
            generate_migration_poscars(run_ini_end_dir, element, idx, new_atoms, vasp_files_dir, position)


def generate_migration_poscars(run_ini_end_dir, vac_element, vac_idx, atoms, vasp_files_dir, vac_position):
    # 获取空位的近邻原子索引
    neighbors, distances = get_vacancy_neighbors(atoms, vac_position, atoms.get_cell(), atoms.pbc)

    # 检查最近邻距离是否超过晶格常数
    lattice_constant = atoms.get_cell().lengths().max()
    for distance in distances:
        if np.any(distance > lattice_constant):
            user_input = input(
                f"Neighbor distance {distance:.2f} exceeds lattice constant {lattice_constant:.2f}. Do you want to continue? (y/n): ")
            if user_input.lower() != 'y':
                print("Terminating the process.")
                return

    # 生成每个近邻交换后的POSCAR文件
    for neighbor_idx in neighbors:
        mig_atoms = atoms.copy()

        # 获取交换原子的元素类型和位置
        mig_element = mig_atoms[neighbor_idx].symbol

        # 交换原子位置
        mig_atoms[neighbor_idx].position, vac_position = vac_position, mig_atoms[neighbor_idx].position

        # 创建NEB运行目录
        neb_run_subdir = os.path.join(run_ini_end_dir,
                                      f"mig_vac_{vac_element}_{vac_idx}_to_{mig_element}_{neighbor_idx}")
        if not os.path.exists(neb_run_subdir):
            os.makedirs(neb_run_subdir)
        print(f"Creating NEB run directory: {neb_run_subdir}")

        # 生成新的POSCAR文件名
        mig_poscar_file = os.path.join(neb_run_subdir, 'POSCAR_end')

        # 写入新的POSCAR文件
        write(mig_poscar_file, mig_atoms, format='vasp')
        print(
            f"Generated migration POSCAR {mig_poscar_file} with vacancy {vac_element} at index {vac_idx} swapped with {mig_element} at index {neighbor_idx}")

        # 复制必要的VASP文件到NEB运行目录
       # for file_name in ['INCAR', 'POTCAR', 'KPOINTS']
        for file_name in ['INCAR', 'POTCAR']:
            src_file_path = os.path.join(vasp_files_dir, file_name)
            dst_file_path = os.path.join(neb_run_subdir, file_name)
            shutil.copy(src_file_path, dst_file_path)

        print(f"Copied necessary VASP files to NEB run directory: {neb_run_subdir}")


def get_vacancy_neighbors(atoms, vacancy_position, cell, pbc):
    # 计算与空位的距离，考虑周期性边界条件
    all_distances = atoms.positions - vacancy_position
    distances, _ = find_mic(all_distances, cell, pbc)
    scalar_distances = np.linalg.norm(distances, axis=1)

    # 排序并获取最近的12个邻居
    sorted_indices = np.argsort(scalar_distances)
    first_neighbor_indices = sorted_indices[:12]
    sorted_distances = scalar_distances[first_neighbor_indices]

    # 打印近邻信息
    for idx, distance in zip(first_neighbor_indices, sorted_distances):
        print(f"Neighbor index: {idx}, Distance: {distance}")

    return first_neighbor_indices, sorted_distances


# 示例使用
poscar_file = 'POSCAR_4_3_4'  # 替换为你的POSCAR文件路径
generate_poscars_with_vacancies_and_neb(poscar_file)
