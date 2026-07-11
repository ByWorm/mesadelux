# Writer simples para SSD1306 com fonte bitmap variável
# Compatível com font8x16.py

class Writer:
    def __init__(self, oled, font):
        self.oled = oled
        self.font = font

    def text(self, s, x, y):
        """Desenha string na posição (x, y). Devolve largura total usada."""
        cx = x
        for ch in s:
            glyph, w = self.font.get_ch(ch)
            h = self.font.height()
            for row in range(h):
                byte = glyph[row]
                for col in range(8):
                    if byte & (0x80 >> col):
                        px = cx + col
                        py = y + row
                        if 0 <= px < 128 and 0 <= py < 64:
                            self.oled.pixel(px, py, 1)
            cx += w + 1
        return cx - x

    def width(self, s):
        """Calcula largura em pixeis de uma string."""
        return sum(self.font.get_ch(c)[1] + 1 for c in s) - 1

    def cx(self, s):
        """Posição x para centrar s no ecrã de 128px."""
        return max(0, (128 - self.width(s)) // 2)
