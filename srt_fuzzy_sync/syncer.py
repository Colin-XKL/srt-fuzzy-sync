import re
from typing import List

import click as click
import pysrt
from pysrt import SubRipItem
from rapidfuzz import fuzz

MIN_VALID_STR_LEN = 4
MAX_VALID_SUB_STR_LEN_RATIO = 4


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


def text_similarity_calc(str_a, str_b):
    return fuzz.partial_ratio(str_a, str_b)


def is_matched(text_a: str, text_b: str, threshold: float = 0.9) -> bool:
    str_a = text_clean(text_a)
    str_b = text_clean(text_b)

    # ignore strings that are too short
    if min(len(str_a), len(str_b), len(str_a.split(" ")), len(str_b.split(" "))) < MIN_VALID_STR_LEN:
        return False
    if (max(len(str_a), len(str_b)) / min(len(str_a), len(str_b))) > MAX_VALID_SUB_STR_LEN_RATIO:
        return False

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

    last_offset = ref_sub_seq[ref_seq_last_processed_index].TimeStamp - target_sub_seq[
        target_seq_last_processed_index].TimeStamp

    if target_seq_last_processed_index < len(ret_target_time_seq) - 1:
        for index_k in range(target_seq_last_processed_index, len(ret_target_time_seq)):
            ret_target_time_seq[index_k] += last_offset

    return ret_target_time_seq


def get_time_stamp(srt_item: SubRipItem):
    """
    get time stamp for srt item, for sorting
    """
    return srt_item.start.ordinal


@click.group()
def cli():
    pass


@cli.command()
@click.option("-r", "--reference_sub", type=str, required=True, help="reference srt sub file path")
@click.option("-t", "--to_be_sync_sub", type=str, required=True, help="target to be syned srt sub file path")
@click.option("-o", "--output_path", type=str, required=True, help="output srt file path")
def run_sync(reference_sub: str,
             to_be_sync_sub: str,
             output_path: str):
    # read file
    ref = pysrt.open(reference_sub)
    target = pysrt.open(to_be_sync_sub)
    # sort srt
    ref.sort(key=get_time_stamp)
    target.sort(key=get_time_stamp)
    ref_seq = [SubItem(content=item.text, time_stamp=item.start.ordinal) for item in ref]
    target_seq = [SubItem(content=item.text, time_stamp=item.start.ordinal) for item in target]
    match_result = calc_match_result(ref_seq, target_sub_seq=target_seq)
    result_target_time_seq = align_seq(ref_seq, target_seq, match_result)
    print(f"INFO: ref sub: {len(ref)} items")
    print(f"INFO: target sub: {len(target)} items")
    print(f"INFO: matched: {len(match_result)} items")
    if (len(match_result)) < 0.5 * (min(len(ref), len(target))):
        print(
            "WARNING: "
            "not enough matched subtitles, make sure the reference and the target sub are for the same episode.")
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
