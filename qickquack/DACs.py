class DAC ():
    def __init__(self, the_soc):
        self.soc = the_soc

    def init_DAC(self, demux = 0):
        self.soc.axi_pvp_gen_v7_0.send_arbitrary_SPI(demux_int = demux, reg = 0b0010, data_int = 0b0000_0000_0000_0011_0010)
        
    
    def set_DAC(self, demux = 0, volts = 0.0):
        val = volt2reg(volts)
        #5 bits of demux, 4 bits of reg, 20 bits of data
        self.soc.axi_pvp_gen_v7_0.send_arbitrary_SPI(demux, 0b0001, val)


# this function doesn't need a class
def volt2reg(volt = 0.0):
        """Calculates 20 bit representation of voltage based on DAC rails"""
        VREFN = 0.0
        VREFP = 5.0
        bit_res = 20

        if volt < VREFN:
            print("volt out of range, volt < VREFN")
            return -1
        elif volt > VREFP:
            print("volt out of range, volt > VREFP")
            return -1
        else:
            Df = (2**bit_res - 1)*(volt - VREFN)/(VREFP - VREFN)
            print("Df is " + str(bin(int(Df))))
            return int(Df)