# echo
# echo "===== TRI1 (first triphone pass) TRAINING ====="
# echo
# steps/train_deltas.sh --cmd "$train_cmd" 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1
# echo
# echo "===== TRI1 (first triphone pass) DECODING ====="
# echo
# utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1
# steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri1/graph data/test exp/tri1/decode

echo
echo "===== TRI1 ALIGNMENT ====="
echo
steps/align_si.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/tri1 exp/tri1_ali || exit 1;

echo
echo "===== TRI2 (second triphone pass) TRAINING ====="
echo
steps/train_deltas.sh --cmd "$train_cmd" 2500 15000 data/train data/lang exp/tri1_ali exp/tri2a || exit 1;

echo
echo "===== TRI2 (second triphone pass) DECODING ====="
echo
utils/mkgraph.sh data/lang exp/tri2a exp/tri2a/graph || exit 1
steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri2a/graph data/test exp/tri2a/decode

echo
echo "===== TRI2 ALIGNMENT ====="
echo
steps/align_si.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/tri2a exp/tri2a_ali || exit 1;

echo
echo "===== LDA-MLLT TRAINING ====="
echo
steps/train_lda_mllt.sh --cmd "$train_cmd" 3500 20000 data/train data/lang exp/tri2a_ali exp/tri3a || exit 1;

echo
echo "===== LDA-MLLT DECODING ====="
echo
utils/mkgraph.sh data/lang exp/tri3a exp/tri3a/graph || exit 1
steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri3a/graph data/test exp/tri3a/decode

echo
echo "===== LDA-MLLT ALIGNMENT ====="
echo
steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/tri3a exp/tri3a_ali || exit 1;

# echo
# echo "===== SAT TRI TRAINING ====="
# echo
# steps/train_sat.sh  --cmd "$train_cmd" 4200 40000 data/train data/lang exp/tri3a_ali exp/tri4a || exit 1;

# echo
# echo "===== SAT TRI DECODING ====="
# echo
# utils/mkgraph.sh data/lang exp/tri4a exp/tri4a/graph || exit 1
# steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri4a/graph data/test exp/tri4a/decode

# echo
# echo "===== SAT TRI ALIGNMENT ====="
# echo
# steps/align_fmllr.sh  --cmd "$train_cmd" \
# data/train data/lang exp/tri4a exp/tri4a_ali || exit 1;
