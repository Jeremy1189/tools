# 步骤1: 检索当前目录下的所有子目录
directories=($(find . -mindepth 1 -maxdepth 1 -type d | sort))

# 如果没有找到任何目录，则退出脚本
if [ ${#directories[@]} -eq 0 ]; then
    echo "No directories found in the current directory."
    exit 1
fi

# 显示所有检索到的目录并进行编号
echo "Available directories:"
for i in "${!directories[@]}"; do
    echo "$((i+1)). ${directories[i]}"
done

# 步骤2: 用户输入要提交的目录编号
echo "Enter the numbers of the directories you want to submit, separated by spaces or commas (e.g., 1, 2, 5 or 1 2 5):"
read -r input

# 处理用户输入，支持逗号和空格作为分隔符
input_indexes=(${input//,/ })

# 确定并验证用户选择的目录
selected_dirs=()
for index in "${input_indexes[@]}"; do
    if (( index > 0 && index <= ${#directories[@]} )); then
        selected_dirs+=("${directories[index-1]}")
    else
        echo "Warning: Invalid directory number $index"
    fi
done

# 步骤3: 定义各种提交命令，并允许用户选择
declare -a submit_commands=("$HOME/bin/sub_vasp_gpu_v100" "$HOME/bin/batch_sub_vasp" "$HOME/bin/sub_vasp_gpu_a100" "$HOME/bin/batch_sub_vasp" "../neb_batch_sub_vasp" )

echo "Select the submission method:"
echo "1. sbatch $HOME/bin/sub_vasp_gpu_v100"
echo "2. sbatch $HOME/bin/batch_sub_vasp"
echo "3. sbatch $HOME/bin/sub_vasp_gpu_a100"
echo "4. sbatch $HOME/bin/tiny_sub_vasp"
echo "5. sbatch ../neb_batch_sub_vasp"
read -r method_index
# 验证用户选择的提交方法是否有效
if [[ $method_index -lt 1 || $method_index -gt 5 ]]; then
    echo "Invalid submission method selected. Exiting."
    exit 1
fi

# 显示用户的选择
selected_method="${submit_commands[$((method_index-1))]}"
echo "You have selected to submit the following directories with the method '$selected_method':"
for dir in "${selected_dirs[@]}"; do
    echo "$dir"
done

# 步骤4: 确认是否继续提交
echo "Do you want to proceed with the submission? (yes/no)"
read -r confirmation

if [[ $confirmation == "yes" ]]; then
    for dir in "${selected_dirs[@]}"; do
        echo "Preparing to submit job in directory $dir..."
        # 复制 POSCAR_end 为 POSCAR
        cp "$dir/POSCAR_end" "$dir/POSCAR"
        # 进入目录并提交任务
        cd "$dir"
        sbatch $selected_method
        cd ..
        echo "Submitted job in directory $dir"
    done
else
    echo "Submission cancelled."
fi
