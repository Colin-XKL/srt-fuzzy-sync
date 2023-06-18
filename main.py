import re
from typing import List

import pysrt
from rapidfuzz import fuzz


def text_similarity_calc(str_a, str_b):
    return fuzz.partial_ratio(str_a, str_b)


def is_matched(text_a: str, text_b: str, threshold: float = 0.9) -> bool:
    str_a = text_clean(text_a)
    str_b = text_clean(text_b)
    normalized_score = (text_similarity_calc(str_a, str_b)) / 100
    # print("score:", normalized_score)
    return normalized_score > threshold


def text_clean(input_str: str) -> str:
    # Remove HTML or XML tags
    cleaned = re.sub(r'<[^<]+?>', '', input_str)
    # remove {} tags
    cleaned = re.sub(r'{[^<]+?}', "", cleaned)

    # Convert to lower case
    cleaned = cleaned.lower()

    cleaned.replace("\n", " ").replace("  ", " ")
    return cleaned.strip()


class MatchResult:
    refSeqIndex: int
    targetSeqIndex: int

    def __init__(self, ref_seq_index, target_seq_index):
        self.refSeqIndex = ref_seq_index
        self.targetSeqIndex = target_seq_index


class SubItem:
    # Index: int
    TimeStamp: float
    OriginalContent: str

    def __init__(self, time_stamp, content: str):
        self.TimeStamp = time_stamp
        self.OriginalContent = content


def calc_match_result(ref_sub_seq: List[SubItem], target_sub_seq: List[SubItem]) -> List[MatchResult]:
    last_matched_index_j = 0

    ret = []
    for indexI in range(0, len(ref_sub_seq)):
        for indexJ in range(last_matched_index_j, len(target_sub_seq)):
            if is_matched(ref_sub_seq[indexI].OriginalContent, target_sub_seq[indexJ].OriginalContent):
                # print("got matched")
                # print(ref_sub_seq[indexI].OriginalContent)
                # print(target_sub_seq[indexJ].OriginalContent)
                match_item = MatchResult(
                    ref_seq_index=indexI,
                    target_seq_index=indexJ
                )
                last_matched_index_j = indexJ
                ret.append(match_item)

    return ret


def align_seq(ref_sub_seq: List[SubItem], target_sub_seq: List[SubItem], match: List[MatchResult]):
    ref_seq_last_processed_index = 0
    target_seq_last_processed_index = 0

    ret_target_time_seq = [x.TimeStamp for x in target_sub_seq]

    for match_item in match:
        index_i = match_item.refSeqIndex
        index_j = match_item.targetSeqIndex

        old_time_window_start = target_sub_seq[target_seq_last_processed_index].TimeStamp
        old_time_window_end = target_sub_seq[index_j].TimeStamp
        old_time_window_len = old_time_window_end - old_time_window_start

        new_time_window_start = ref_sub_seq[ref_seq_last_processed_index].TimeStamp
        new_time_window_end = ref_sub_seq[index_i].TimeStamp
        new_time_window_len = new_time_window_end - new_time_window_start

        for index_k in range(target_seq_last_processed_index, index_j):
            t = target_sub_seq[index_k].TimeStamp

            percent = (t - old_time_window_start) / old_time_window_len

            new_t = new_time_window_len * percent + new_time_window_start

            ret_target_time_seq[index_k] = new_t

        ref_seq_last_processed_index = index_i
        target_seq_last_processed_index = index_j
    return ret_target_time_seq


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
    # read file
    ref = pysrt.open(reference_sub)
    target = pysrt.open(to_be_sync_sub)

    ref_seq = [SubItem(content=item.text, time_stamp=item.start.ordinal) for item in ref]
    target_seq = [SubItem(content=item.text, time_stamp=item.start.ordinal) for item in target]

    match_result = calc_match_result(ref_seq, target_sub_seq=target_seq)
    result_target_time_seq = align_seq(ref_seq, target_seq, match_result)

    for index in range(len(target)):
        new_time_ordinal = result_target_time_seq[index]

        old_time_start = target[index].start
        old_time_end = target[index].end
        new_time_start = pysrt.SubRipTime.from_ordinal(new_time_ordinal)
        new_time_end = pysrt.SubRipTime.from_ordinal(new_time_ordinal + (old_time_end.ordinal - old_time_start.ordinal))

        target[index].start = new_time_start
        target[index].end = new_time_end
    # output
    target.save(output_path, encoding='utf-8')
    print('done.')
    print("new sub file saved to ", output_path)
