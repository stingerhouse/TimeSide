# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Paul Brossier <piem@piem.org>

# This file is part of TimeSide.

# TimeSide is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# TimeSide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.

# Author: Paul Brossier <piem@piem.org>

from timeside.core import Processor, implements, interfacedoc, FixedSizeInputAdapter
from timeside.analyzer.core import *
from timeside.api import IValueAnalyzer

import numpy
from aubio import filterbank, pvoc

class AubioMelEnergy(Processor):
    implements(IValueAnalyzer)

    @interfacedoc
    def setup(self, channels=None, samplerate=None, blocksize=None, totalframes=None):
        super(AubioMelEnergy, self).setup(channels, samplerate, blocksize, totalframes)
        self.win_s = 1024
        self.hop_s = self.win_s / 4
        self.n_filters = 40
        self.n_coeffs = 13
        self.pvoc = pvoc(self.win_s, self.hop_s)
        self.melenergy = filterbank(self.n_filters, self.win_s)
        self.melenergy.set_mel_coeffs_slaney(samplerate)
        self.block_read = 0
        self.melenergy_results = numpy.zeros([self.n_filters, ])

    @staticmethod
    @interfacedoc
    def id():
        return "aubio_mel_analyzer"

    @staticmethod
    @interfacedoc
    def name():
        return "Mel Energy analysis (aubio)"

    def process(self, frames, eod=False):
        for samples in downsample_blocking(frames, self.hop_s):
            fftgrain = self.pvoc(samples)
            self.melenergy_results = numpy.vstack( [ self.melenergy_results, self.melenergy(fftgrain) ])
            self.block_read += 1
        return frames, eod

    def results(self):

        container = AnalyzerResultContainer()

        melenergy = AnalyzerResult(id = "aubio_melenergy", name = "melenergy (aubio)", unit = "")
        melenergy.value = self.melenergy_results
        container.add_result(melenergy)

        melenergy_mean = AnalyzerResult(id = "aubio_melenergy_mean", name = "melenergy mean (aubio)", unit = "")
        melenergy_mean.value = numpy.mean(self.melenergy_results,axis=0)
        container.add_result(melenergy_mean)

        melenergy_median = AnalyzerResult(id = "aubio_melenergy_median", name = "melenergy median (aubio)", unit = "")
        melenergy_median.value = numpy.median(self.melenergy_results,axis=0)
        container.add_result(melenergy_median)

        return container

