"""
FITS-specific miscellaneous functions
"""

#-----------------------------------------------------------------------------
# Copyright (c) 2014, yt Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

from .data_structures import ap
from yt.funcs import ensure_list, fix_axis
pyfits = ap.pyfits
pywcs = ap.pywcs

axis_wcs = [[1,2,0],[0,2,1],[0,1,2]]

class FITSFile(pyfits.HDUList):
    def __init__(self, ds, data_source, fields, axis):
        super(FITSFile, self).__init__()
        self.ds = ds
        self.fields = fields
        self.axis = axis
        ndims = ds.dimensionality
        dims = ds.domain_dimensions
        nx, ny = dims[axis_wcs[axis][0]], dims[axis_wcs[axis][1]]
        self._frb = data_source.to_frb((1.0,"unitary"), (nx,ny))
        w = pywcs.WCS(naxis=ndims)
        w.wcs.crpix = [self.ds.wcs.wcs.crpix[idx] for idx in axis_wcs[axis][:ndims]]
        w.wcs.cdelt = [self.ds.wcs.wcs.cdelt[idx] for idx in axis_wcs[axis][:ndims]]
        w.wcs.crval = [self.ds.wcs.wcs.crval[idx] for idx in axis_wcs[axis][:ndims]]
        w.wcs.cunit = [str(self.ds.wcs.wcs.cunit[idx]) for idx in axis_wcs[axis][:ndims]]
        w.wcs.ctype = [self.ds.wcs.wcs.ctype[idx] for idx in axis_wcs[axis][:ndims]]
        im = self._frb[fields[0]].ndarray_view()
        if ndims == 3: im = im.reshape(1,nx,ny)
        self.append(pyfits.PrimaryHDU(im, header=w.to_header()))
        if len(fields) > 1:
            for field in fields[1:]:
                im = self._frb[field].ndarray_view()
                if ndims == 3: im = im.reshape(1,nx,ny)
                self.append(pyfits.ImageHDU(im, header=w.to_header()))

    def writeto(self, fileobj, **kwargs):
        pyfits.HDUList(self).writeto(fileobj, **kwargs)

class FITSSlice(FITSFile):
    def __init__(self, ds, axis, fields, coord, **kwargs):
        fields = ensure_list(fields)
        axis = fix_axis(axis)
        slc = ds.slice(axis, coord, **kwargs)
        super(FITSSlice, self).__init__(ds, slc, fields, axis)

class FITSProjection(FITSFile):
    def __init__(self, ds, axis, fields, **kwargs):
        fields = ensure_list(fields)
        axis = fix_axis(axis)
        prj = ds.proj(fields[0], axis, **kwargs)
        super(FITSProjection, self).__init__(ds, prj, fields, axis)


