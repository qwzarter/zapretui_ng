from typing import List


def get_script_parameters(game_mode_checked: bool, lists_dir: str, bin_dir: str, mode: str) -> List[str]:
    if game_mode_checked:
        game_filter = "1024-65535"
    else:
        game_filter = "12"

    base_params = [
        f"--wf-tcp=80,443,2053,2083,2087,2096,8443,{game_filter}",
        f"--wf-udp=443,19294-19344,50000-50100,{game_filter}"
    ]

    base_filters = [
        '--filter-udp=443', '--hostlist', f'{lists_dir}/list-general.txt',
        '--dpi-desync=fake', '--dpi-desync-repeats=6',
        '--dpi-desync-fake-quic', f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

        '--filter-udp=19294-19344,50000-50100', '--filter-l7=discord,stun',
        '--dpi-desync=fake', '--dpi-desync-repeats=6', '--new',

        '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
        '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new'
    ]

    mode_params = {
        "Стандартный": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
            '--dpi-desync-repeats=8', '--dpi-desync-fooling=md5sig,badseq', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
            '--dpi-desync-repeats=8', '--dpi-desync-fooling=md5sig,badseq', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            '--dpi-desync-fake-quic', f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2',
            '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
            '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig,badseq', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1',
            '--dpi-desync-fake-unknown-udp', f'{bin_dir}/quic_initial_www_google_com.bin',
            '--dpi-desync-cutoff=n2'
        ],

        "ALT": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            '--dpi-desync-fake-quic', f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp', f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
        ],

        "ALT2 (Рекомендуемый)": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp', f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "ALT3": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
            '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
            '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
            '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "ALT4": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "ALT5": [
            '--filter-l3=ipv4', '--filter-tcp=443,2053,2083,2087,2096,8443', '--dpi-desync=syndata', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=14',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
        ],

        "ALT6": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "ALT7": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            "--dpi-desync=multisplit", "--dpi-desync-split-pos=2,sniext+1", "--dpi-desync-split-seqovl=679",
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            "--dpi-desync=multisplit", "--dpi-desync-split-pos=2,sniext+1", "--dpi-desync-split-seqovl=679",
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-tcp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=syndata', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "ALT8": [
            '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,split2', '--dpi-desync-autottl=2', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--new',

            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,split2', '--dpi-desync-autottl=2', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=2', '--new',

            '--filter-tcp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=syndata', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "FAKE TLS AUTO": [
            '--filter-udp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
            '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
            '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
            '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
            '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "FAKE TLS AUTO ALT": [
            '--filter-udp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
            '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
            '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "FAKE TLS AUTO ALT2": [
            '--filter-udp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
            '--dpi-desync-split-seqovl-pattern', f'{bin_dir}/tls_clienthello_www_google_com.bin',
            '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "FAKE TLS AUTO ALT3": [
            '--filter-udp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
            '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
            '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
            '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
            '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ],

        "SIMPLE FAKE (MGTS)": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
            '--dpi-desync-fake-tls', f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
        ],

        "SIMPLE FAKE ALT (MGTS ALT)": [
            '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-tcp=443', '--hostlist', f'{lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            '--filter-udp=443', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-tcp=80', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

            f'--filter-tcp=443,{game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
            '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
            f'{bin_dir}/tls_clienthello_www_google_com.bin', '--new',

            f'--filter-udp={game_filter}', '--ipset', f'{lists_dir}/ipset-all.txt',
            '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
            '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
            f'{bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
        ]
    }

    params = base_params + base_filters
    if mode in mode_params:
        params += mode_params[mode]

    return params
