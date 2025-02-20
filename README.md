# tools
some tools for data analysis and handling

#“get_type_raw_paths.sh说明：
脚本功能：该脚本会搜索指定文件夹（或当前目录，如果未提供路径）中所有包含 type.raw 文件的文件夹，并输出这些文件夹的相对路径到一个 .txt 文件中。每个路径将用引号包裹，并且多个路径之间用逗号分隔。

输出格式：输出文件中的路径格式如下：

arduino
Copy
"relative/path/to/folder", 
"another/folder/path", 
最后一行没有额外的逗号，并且换行。

如何运行：

脚本接受一个文件夹路径作为参数，或者如果没有提供路径，将提示用户选择文件夹。
示例：
bash
Copy
./get_type_raw_paths.sh ./data_folder”
