from EthHasher import contract, read_write
from EthHasher import machine_learning

ct = contract()
rw = read_write()
ml = machine_learning()

#ml.get_cluster_arr()
#ml.cluster_addresses()
#ml.cluster_gen(ml.format_names(ml.cluster_names()))
#ml.bar_graph_gen(ml.word_freq(ml.clean_names(ml.format_names(ml.cluster_names())), c_len=2, cutoff=0.5))
#ml.format_names(ml.cluster_names())
#ml.scatter_graph_gen(ml.cluster_count(), ml.word_freq(ml.clean_names(ml.format_names(ml.cluster_names())), c_len=0, cutoff=0))

ml.bar_graph_words(ml.name_set_freq(50))

#ml.cluster()
#ml.word_freq(ml.clean_names(ml.format_names(ml.cluster_names())), c_len=0, cutoff=0)
#ml.cloud_gen_simple(ml.name_set_freq())

#------------------------------------------------------------------------------------
#----Uncomment line below to get new address list from etherscan.io and write to file-----#
#Replace N with number of pages of verfied contracts to acquire
#WARNING: Overwrites existing 'address_list.txt'
#rw.addresses_to_file(ct.get_address_list(N))
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to get bytecode from etherchain.org and write to file----#
#WARNING: Overwrites existsing 'bytecode_list.txt'
#rw.bytecode_to_file(ct.get_bytecode(rw.addresses_from_file("address_list.txt")))
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to generate and store hashes----#
#WARNING: Overwrites 'hash_list.txt'
#rw.hashes_to_file(ct.get_hashes(rw.bytecode_from_file("bytecode_list.txt")))
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to clean data----#
#WARNING: Overwrites 'clean' version of .txt files
#rw.clean_data()
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to carry out affinity propagation----#
#Expects 'hash_list_clean.txt' to be present
#ml.cluster()
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to generate graph from clusters----#
#ml.graph_gen(ml.cluster_count())
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#----Uncomment line below to create file with names and corrisponding addresses----#
#N.B: json_opt can be set to false for human readable output
#rw.name_dict_to_file(ct.get_names(rw.addresses_from_file("address_list_clean.txt")), json_opt=True)
#------------------------------------------------------------------------------------