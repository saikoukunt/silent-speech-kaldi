. ./path.sh || exit 1
. ./cmd.sh || exit 1

nj=1
utils/fix_data_dir.sh data/test
mfccdir=mfcc
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/test exp/make_mfcc/test $mfccdir
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir

steps/decode.sh --skip-scoring true --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri3a/graph data/test exp/tri3a/decode


dir=exp/tri3a/decode

mkdir -p $dir/scoring/log

lattice-best-path --lm-scale=13 --word-symbol-table=data/lang/words.txt  "ark:gunzip -c $dir/lat.1.gz|" ark,t:$dir/13.tra || exit 1;

utils/int2sym.pl -f 2- data/lang/words.txt exp/tri3a/decode/13.tra >> output.txt        
