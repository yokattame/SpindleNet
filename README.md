# SpindleNet

    mkdir external
    cd external
    ln -sf /path/to/the/root/of/datasets raw_data
    ln -sf /path/to/your/experiments/directory exp
    cd ..
    ./scripts/format_rawdata.sh
    ./scripts/make_datalists.sh
    ./scripts/merge_datalists.sh
    ./scripts/gen_proposal_datalist.sh

    ./scripts/train_base.sh
    
    ./scripts/train_head.sh
    ./scripts/train_body.sh
    ./scripts/train_leg.sh
    ./scripts/train_rarm.sh
    ./scripts/train_larm.sh
    ./scripts/train_rleg.sh
    ./scripts/train_lleg.sh

    ./scripts/train_spindlenet.sh

    ./scripts/test.sh
