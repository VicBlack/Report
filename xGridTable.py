#coding=utf-8
import wx.grid as grid


class ReportInfoGridTable(grid.GridTableBase):
    def __init__(self, datas, colLabels):
        grid.GridTableBase.__init__(self)
        self.datas = datas
        self.colLabels = colLabels
        self.odd = grid.GridCellAttr()
        self.odd.SetReadOnly(True)
        self.even = grid.GridCellAttr()
        self.even.SetReadOnly(True)
        pass

    def GetAttr(self, row, col, kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    def GetNumberRows(self):
        return len(self.datas)

    def GetNumberCols(self):
        return len(self.colLabels)

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return str(row)

    def GetValue(self, row, col):
        return self.datas[row][col]

    def DeleteRows(self, rowindex=0, numRows=1):
        for i in range(rowindex, rowindex + numRows):
            self.datas.pop(rowindex)
        return True

    def AppendRows(self, rows):
        self.datas.extend(rows)
        return True

    def PopData(self, index):
        return self.datas.pop(index)