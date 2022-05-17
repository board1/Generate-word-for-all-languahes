# 这是一个针对所有有单词边界或者没有单词边界的语言都可以使用的 分词算法

算法可以自动检测是否包含单词边界从而调用不同处理模块

使用时替换main_文件中的路径即可
这里的计算指标包括 左右信息熵 词频和凝固度
其中凝固度越高，该gram 越有可能是一个 word/phrase

# This is a tokenization algorithm that can be used for all languages with or without word boundaries

Algorithms can automatically detect whether word boundaries are included and call different processing modules

When using, replace the path in the main_ file
The calculation indicators here include left and right information entropy, word frequency and coagulation degree
The higher the degree of solidification, the more likely the gram is a word/phrase