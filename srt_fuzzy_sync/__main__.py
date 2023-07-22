import pysrt
from srt_fuzzy_sync.syncer import SubItem, calc_match_result, align_seq, get_time_stamp, run_sync

if __name__ == '__main__':
    import sys

    args = sys.argv
    if len(args) != 4:
        print("ERR: arg num error. expect 3 (reference srt, target to be synced srt, output srt file)")
        sys.exit(-1)

    print('start')
    # set input file path
    reference_sub = args[1]
    to_be_sync_sub = args[2]
    output_path = args[3]
    run_sync(reference_sub=reference_sub, to_be_sync_sub=to_be_sync_sub, output_path=output_path)
