from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import fontforge  # noqa
import os
import multiprocessing as mp
import argparse

# conda deactivate
# apt install python3-fontforge

def convert_mp(opts):
    """Useing multiprocessing to convert all fonts to sfd files"""
    ltn_chars = opts.ltn_alphabet
    cyr_chars = opts.cyr_alphabet
    cyr_names = opts.cyr_codes
    cyr_uni = opts.cyr_unicodes
    fonts_file_path = opts.ttf_path
    sfd_path = opts.sfd_path
    for root, dirs, files in os.walk(os.path.join(opts.ttf_path, opts.split)):
        ttf_fnames = files
    #print(ttf_fnames)
    font_num = len(ttf_fnames)
    process_nums = mp.cpu_count() - 2
    if font_num // process_nums < 1:
        process_nums = font_num
        font_num_per_process = min(font_num // process_nums, 1)
    else:
        font_num_per_process = font_num // process_nums

    def process(process_id, font_num_p_process):
        for i in range(process_id * font_num_p_process, (process_id + 1) * font_num_p_process):
            if i >= font_num:
                break
            
            font_id = ttf_fnames[i].split('.')[0]
            split = opts.split
            font_name = ttf_fnames[i]
            
            font_file_path = os.path.join(fonts_file_path, split, font_name)
            try:
                cur_font = fontforge.open(font_file_path)
            except Exception as e:
                print('Cannot open', font_name)
                print(e)
                continue

            target_dir = os.path.join(sfd_path, split, "{}".format(font_id))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            #latin processing
            for char_id, char in enumerate(ltn_chars):
                char_description = open(os.path.join(target_dir, '{}_{:02d}.txt'.format(font_id, char_id)), 'w')

                cur_font.selection.select(char)
                cur_font.copy()

                new_font_for_char = fontforge.font()
                new_font_for_char.selection.select(char)
                new_font_for_char.paste()
                new_font_for_char.fontname = "{}_".format(font_id) + font_name

                new_font_for_char.save(os.path.join(target_dir, '{}_{:02d}.sfd'.format(font_id, char_id)))

                char_description.write(str(ord(char)) + '\n')
                char_description.write(str(new_font_for_char[char].width) + '\n')
                char_description.write(str(new_font_for_char[char].vwidth) + '\n')
                char_description.write('{:02d}'.format(char_id) + '\n')
                char_description.write('{}'.format(font_id))

                char_description.close()
            
            #cyrillic processing
            for char_id, char in enumerate(cyr_names): 
                char_description = open(os.path.join(target_dir, '{}_{:02d}.txt'.format(font_id, char_id+52)), 'w')

                cur_font.selection.select(char)
                cur_font.copy()

                new_font_for_char = fontforge.font()
                new_font_for_char.createChar(cyr_uni[char_id], char)
                new_font_for_char.selection.select(cyr_names[char_id])
                new_font_for_char.paste()
                new_font_for_char.fontname = "{}_".format(font_id) + font_name

                new_font_for_char.save(os.path.join(target_dir, '{}_{:02d}.sfd'.format(font_id, char_id+52)))

                char_description.write(str(ord(cyr_chars[char_id])) + '\n')
                char_description.write(str(new_font_for_char[char].width) + '\n')
                char_description.write(str(new_font_for_char[char].vwidth) + '\n')
                char_description.write('{:02d}'.format(char_id+52) + '\n')
                char_description.write('{}'.format(font_id))

                char_description.close()

            cur_font.close()

    processes = [mp.Process(target=process, args=(pid, font_num_per_process)) for pid in range(process_nums + 1)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()


def main():
    parser = argparse.ArgumentParser(description="Convert ttf fonts to sfd fonts")
    parser.add_argument("--ltn_alphabet", type=str, default='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    parser.add_argument("--cyr_alphabet", type=str, default='БГДЁЖЗИЙЛПФЦЧШЩЪЫЬЭЮЯбвгдёжзийклмнптфцчшщъыьэюя')
    parser.add_argument("--cyr_codes", type=list, default=['afii10018', 'afii10020', 'afii10021', 'afii10023', 'afii10024', 'afii10025', 'afii10026', 'afii10027', 'afii10029', 'afii10033', 'afii10038', 'afii10040', 'afii10041', 'afii10042', 'afii10043', 'afii10044', 'afii10045', 'afii10046', 'afii10047', 'afii10048', 'afii10049', 'afii10066', 'afii10067', 'afii10068', 'afii10069', 'afii10071', 'afii10072', 'afii10073', 'afii10074', 'afii10075', 'afii10076', 'afii10037', 'afii10078', 'afii10079', 'afii10081', 'afii10084', 'afii10086', 'afii10088', 'afii10089', 'afii10090', 'afii10091', 'afii10092', 'afii10093', 'afii10094', 'afii10095', 'afii10096', 'afii10097'])
    parser.add_argument("--cyr_unicodes", type=list, default=[0x411, 0x413, 0x414, 0x401, 0x416, 0x417, 0x418, 0x419, 0x41B, 0x41F, 0x424, 0x426, 0x427, 0x428, 0x429, 0x42A, 0x42B, 0x42C, 0x42D, 0x42E, 0x42F, 0x431, 0x432, 0x433, 0x434, 0x451, 0x436, 0x437, 0x438, 0x439, 0x43A, 0x43B, 0x43C, 0x43D, 0x43F, 0x442, 0x444, 0x446, 0x447, 0x448, 0x449, 0x44A, 0x44B, 0x44C, 0x44D, 0x44E, 0x44F])
    parser.add_argument("--ttf_path", type=str, default='font_ttfs')
    parser.add_argument('--sfd_path', type=str, default='font_sfds')
    parser.add_argument('--split', type=str, default='train')
    opts = parser.parse_args()

    convert_mp(opts)


if __name__ == "__main__":
    main()
