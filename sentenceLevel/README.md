1. 根据已有的百科知识点，从百度上爬去one hop的知识点，然后人工筛选出与初中数学有关的知识点。
2. 根据获得的知识点，从百度百科爬去内容，然后从中找出同时包含两个或两个以上的句子，人工标注在这句句子中两个实体之间的关系，作为数据集。
3. 目前关系的类型定义为 无关、正序、逆序、同义、反义、属于、包含、属性等。
4. 以所有分词后的百科文章作为语料，使用word2vec来生成词向量。
5. 使用stanford POS工具对所有语料的句子的单词进行词性标注,并对这个特征进行embedding。
6. 使用stanford parse工具将句子解析成dependency path，然后找出shortest dependency path，将SDP上的单词喂给LSTM。
7. 构建LSTM网络。
8. 对每句句子进行预测，得到一种关系，然后将这些关系整合。或者先挑出一对实体的所有句子，然后对它们进行关系预测，最后通过投票得到最终的关系。