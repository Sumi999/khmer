#! /usr/bin/env python
# This file is part of khmer, https://github.com/dib-lab/khmer/, and is
# Copyright (C) 2012-2015, Michigan State University.
# Copyright (C) 2015, The Regents of the University of California.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the name of the Michigan State University nor the names
#       of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Contact: khmer-project@idyll.org
"""
Use a set of query reads to sweep out overlapping reads from another file.

% python scripts/sweep-reads2.py <query reads> <search reads>

Results end up in <search reads>.sweep2.

Use '-h' for parameter help.
"""
from __future__ import print_function

import sys
import khmer
import os.path
import screed
from khmer.khmer_args import (build_nodegraph_args, DEFAULT_MAX_TABLESIZE)


def main():
    parser = build_construct_args()
    parser.add_argument('input_filename')
    parser.add_argument('read_filename')

    args = parser.parse_args()

    if not args.quiet:
        if args.min_hashsize == DEFAULT_MAX_TABLESIZE:
            print("** WARNING: hashsize is default!  " \
                "You absodefly want to increase this!\n** " \
                "Please read the docs!", file=sys.stderr)

        print('\nPARAMETERS:', file=sys.stderr)
        print(' - kmer size =    %d \t\t(-k)' % args.ksize, file=sys.stderr)
        print(' - n hashes =     %d \t\t(-N)' % args.n_hashes, file=sys.stderr)
        print(' - min hashsize = %-5.2g \t(-x)' % \
            args.min_hashsize, file=sys.stderr)
        print('', file=sys.stderr)
        print('Estimated memory usage is %.2g bytes ' \
            '(n_hashes x min_hashsize / 8)' % (
                args.n_hashes * args.min_hashsize / 8.), file=sys.stderr)
        print('-' * 8, file=sys.stderr)

    K = args.ksize
    HT_SIZE = args.min_hashsize
    N_HT = args.n_hashes

    inp = args.input_filename
    readsfile = args.read_filename

    outfile = os.path.basename(readsfile) + '.sweep2'
    outfp = open(outfile, 'w')

    # create a nodegraph data structure
    ht = khmer.Nodegraph(K, HT_SIZE, N_HT)

    # load contigs, connect into N partitions
    print('loading input reads from', inp)
    ht.consume_fasta(inp)

    print('starting sweep.')

    n = 0
    m = 0
    for record in screed.open(readsfile):
        if len(record.sequence) < K:
            continue

        if n % 10000 == 0:
            print('...', n, m)

        count = ht.get_median_count(record.sequence)[0]
        if count:
            m += 1
            outfp.write('>%s\n%s\n' % (record.name, record.sequence))
        n += 1

if __name__ == '__main__':
    main()

# vim: set ft=python ts=4 sts=4 sw=4 et tw=79:
