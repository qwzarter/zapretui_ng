from typing import List
from pathlib import Path


def get_script_parameters(game_mode_checked: bool, lists_dir: str, bin_dir: str, mode: str) -> List[str]:
    if game_mode_checked:
        game_filter = "1024-65535"
    else:
        game_filter = "12"

    base_params = [
        f"--wf-tcp=80,443,2053,2083,2087,2096,8443,{game_filter}",
        f"--wf-udp=443,19294-19344,50000-50100,{game_filter}"
    ]

    mode_params = {
        "General": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=568', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_4pda_to.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=568', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_4pda_to.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n3'
        ],

        "Alt2": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt3": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,hostfakesplit', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com',
            '--dpi-desync-hostfakesplit-mod=host=www.google.com,altorder=1', '--dpi-desync-fooling=ts', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,hostfakesplit', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com',
            '--dpi-desync-hostfakesplit-mod=host=www.google.com,altorder=1', '--dpi-desync-fooling=ts', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,hostfakesplit', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=ya.ru',
            '--dpi-desync-hostfakesplit-mod=host=ya.ru,altorder=1', '--dpi-desync-fooling=ts', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,hostfakesplit', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=ya.ru',
            '--dpi-desync-hostfakesplit-mod=host=ya.ru,altorder=1', '--dpi-desync-fooling=ts', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt4": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=1000', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=1000', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=1000', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=1000', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt5": [
            '--filter-l3=ipv4', f'--filter-tcp=443,2053,2083,2087,2096,8443,{game_filter}',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=syndata,multidisorder', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=14',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n3'
        ],

        "Alt6": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt7": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-pos=2,sniext+1', '--dpi-desync-split-seqovl=679',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=multisplit', '--dpi-desync-split-pos=2,sniext+1', '--dpi-desync-split-seqovl=679',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-pos=2,sniext+1', '--dpi-desync-split-seqovl=679',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=syndata', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt8": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt9": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=hostfakesplit', '--dpi-desync-repeats=4', '--dpi-desync-fooling=ts',
            '--dpi-desync-hostfakesplit-mod=host=www.google.com', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=hostfakesplit', '--dpi-desync-repeats=4', '--dpi-desync-fooling=ts',
            '--dpi-desync-hostfakesplit-mod=host=www.google.com', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=hostfakesplit', '--dpi-desync-repeats=4', '--dpi-desync-fooling=ts,md5sig',
            '--dpi-desync-hostfakesplit-mod=host=ozon.ru', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=hostfakesplit', '--dpi-desync-repeats=4', '--dpi-desync-fooling=ts',
            '--dpi-desync-hostfakesplit-mod=host=ozon.ru', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt10": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=none', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_4pda_to.bin', '--dpi-desync-fake-tls-mod=none', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fake-tls=!', '--dpi-desync-fake-tls-mod=rnd,sni=www.google.com',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_4pda_to.bin',
            '--dpi-desync-fake-tls-mod=none', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Alt11": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=654', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_max_ru.bin',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_max_ru.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=654', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_max_ru.bin',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_max_ru.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Fake Tls Auto Alt": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--dpi-desync-repeats=8',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--dpi-desync-repeats=8',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--dpi-desync-repeats=8',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--dpi-desync-repeats=8',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Fake Tls Auto Alt2": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Fake Tls Auto Alt3": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=ts', '--dpi-desync-repeats=8',
            f'--dpi-desync-split-seqovl-pattern={bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Fake Tls Auto": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq', '--dpi-desync-fake-tls=0x00000000',
            '--dpi-desync-fake-tls=!', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq', '--dpi-desync-fake-tls=0x00000000',
            '--dpi-desync-fake-tls=!', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq', '--dpi-desync-fake-tls=0x00000000',
            '--dpi-desync-fake-tls=!', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq', '--dpi-desync-fake-tls=0x00000000',
            '--dpi-desync-fake-tls=!', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Simple Fake ALT": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "Simple Fake ALT2": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_max_ru.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_max_ru.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n3'
        ],

        "Simple fake": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', f'--hostlist={lists_dir}/list-google.txt', '--ip-id=zero',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=80,443', f'--hostlist={lists_dir}/list-general.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            f'--dpi-desync-fake-quic={bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-tcp=80,443,{game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--hostlist-exclude={lists_dir}/list-exclude.txt', f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            f'--dpi-desync-fake-tls={bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', f'--ipset={lists_dir}/ipset-all.txt',
            f'--ipset-exclude={lists_dir}/ipset-exclude.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', f'--dpi-desync-fake-unknown-udp={bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n3'
        ]
    }

    params = base_params

    if mode == "Custom":
        try:
            custom_file = Path(lists_dir) / "custom_strategy.txt"
            if custom_file.exists():
                content = custom_file.read_text(encoding='utf-8')
                custom_args = content.split()
                final_args = []
                for arg in custom_args:
                    arg = arg.replace("{bin_dir}", bin_dir)
                    arg = arg.replace("{lists_dir}", lists_dir)
                    final_args.append(arg)
                
                params += final_args
        except Exception:
            pass

    elif mode in mode_params:
        params += mode_params[mode]

    return params