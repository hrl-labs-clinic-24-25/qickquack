class AxiPvpGen(SocIp):
    
    # PVP Gen Control Registers
    
    # START_VAL_0_REG : 20 bit
    # START_VAL_1_REG : 20 bit
    # START_VAL_2_REG : 20 bit
    # START_VAL_3_REG : 20 bit
    
    # TRIGGER_PVP_REG: 1 bit
    
    # DWELL_CYCLES_REG : 16 bit
    # CYCLES_TILL_READOUT : 16 bit
    # STEP_SIZE_REG : 20 bit
    # PVP_WIDTH_REG : 10 bit
    # NUM_DIMS_REG : 3 bits
    
    # DEMUX_0_REG : 6 bit (dac that changes value every cycle) (demuxing)
    # DEMUX_1_REG : 6 bit (dac that changes value every depth^1 cycles)
    # DEMUX_2_REG : 6 bit (dac that changes value every depth^2 cycles)
    # DEMUX_3_REG : 6 bit (dac that changes value every depth^3 cycles)
    
    ## READ_ONLY REGISTER
    # mosi_o : 32 bit
    # select_mux_o: 5 bits
    # readout_o : 1 bit
	# trigger_spi_o: 1 bit
    # done   : 1 bit
    
    
    bindto = ['user.org:user:axi_pvp_gen_v5:4.0']
    
    def __init__(self, description, **kwargs):
        super().__init__(description)
        
        #map register names to offsets
        self.REGISTERS = {
            'START_VAL_0_REG':0, 
            'START_VAL_1_REG':1,
            'START_VAL_2_REG':2,
            'START_VAL_3_REG':3,
        
            'CONFIG_REG':4,
            
            'DWELL_CYCLES_REG':5,
            'CYCLES_TILL_READOUT':6,
            
            'STEP_SIZE_REG':7,
            'PVP_WIDTH_REG':8,
            'NUM_DIMS_REG':9,
            
            'DEMUX_0_REG':10, 
            'DEMUX_1_REG':11,
            'DEMUX_2_REG':12,
            'DEMUX_3_REG':13,
            
            'CTRL_REG':14,
            'MODE_REG':15
        }
        
        #default register values
        self.START_VAL_0_REG = 0
        self.START_VAL_1_REG = 0
        self.START_VAL_2_REG = 0
        self.START_VAL_3_REG = 0
        
        self.CONFIG_REG = 0
        
        self.DWELL_CYCLES_REG = 38400 # at board speed of 384 MHz, 38400 dwell cycles is 100 us
        self.CYCLES_TILL_READOUT = 10
        
        self.STEP_SIZE_REG = 1
        self.PVP_WIDTH_REG = 256
        self.NUM_DIMS_REG = 0 # set to 0 for manual control?
        
        self.DEMUX_0_REG = -1 # if we haven't chosen which demux dac number to be dac_w, then we don't want to accidentally change a random dac by leaving this memory unset
        self.DEMUX_1_REG = -1
        self.DEMUX_2_REG = -1
        self.DEMUX_3_REG = -1
        
        self.CTRL_REG = 14
        self.MODE_REG = 0 #for testing purposes, this will default to mode 3 (manual LDAC) but eventually we'll probably default to 0 (reg step pattern)
        # mosi is read only so we don't give it a default here
        
    def check_lock(self, registerName = "<name of locked register>"):
        if (self.CTRL_REG & 0b1 == 1):
            raise RuntimeError (registerName + " cannot be changed while pvp plot is running.")
    
    def set_start(self, axis = '', start_val = 0b00):
        '''method to set start val 
            (note that we want a method for this because we don't want to worry about registers outside this class)'''
        
        self.check_lock("Start values")
        
        if (axis == '0'):
            self.START_VAL_0_REG = start_val
        elif (axis == '1'):
            self.START_VAL_1_REG = start_val
        elif (axis == '2'):
            self.START_VAL_2_REG = start_val
        elif (axis == '3'):
            self.START_VAL_3_REG = start_val
        else:
            raise ValueError("No valid axis was specified. Valid axis arguments are '0', '1', '2', '3'")
    
    def start_pvp(self):
        self.CTRL_REG |= 0b1
        
    def end_pvp(self):
        self.CTRL_REG &= 0b1110
            
    def set_dwell_cycles(self, dwell_cycles = 38400):
        self.check_lock("Dwell cycles")
        if (dwell_cycles < 1250):
            raise ValueError("Dwell cycles must be at least 1250 so that all SPI messages can send")
        self.DWELL_CYCLES_REG = dwell_cycles
        
    def set_readout_cycles(self, cycles_till = 400):
        '''sets readout cycles'''
        self.check_lock("Readout cycles")
        self.CYCLES_TILL_READOUT = cycles_till
    
    def set_step_size(self, step_size = 0):
        '''sets size of step (in Volts??)'''
        self.check_lock("step size")
        self.STEP_SIZE_REG = step_size
        
    def set_pvp_width(self, pvp_width = 256): #this default value is so if someone accidentally runs the method without a argument, the new value is just the default reset value
        '''sets the width in pixels of a pvp'''
        self.check_lock("Pvp width")
        self.PVP_WIDTH_REG = pvp_width
        
    def set_num_dims(self, num_dims = 0):
        '''sets the number of dacs looped through in the pvp plot'''
        self.check_lock("Number of dimensions")
        self.NUM_DIMS_REG = num_dims
        
    def set_demux(self, axis = '', demux = -1): 
        self.check_lock("Demux values")
        
        init_DAC(demux)
        
        #note to self: do we specify demux value or ask for board num and dac num?
        if (demux >= 0 and demux < 32):
            if (axis == '0'):
                self.DEMUX_0_REG = demux
            elif (axis == '1'):
                self.DEMUX_1_REG = demux
            elif (axis == '2'):
                self.DEMUX_2_REG = demux
            elif (axis == '3'):
                self.DEMUX_3_REG = demux
            else:
                raise ValueError("No valid axis was specified. Valid axis arguments are '0', '1', '2', '3'")
        else:
            raise ValueError("Demux value must be in the range 0-31 inclusive")
            
    def set_mode(self, m = 0):
        self.check_lock("Mode")
        if (m < 0 or m > 3):
            raise ValueError("Mode must be 0b00, 0b01, 0b10, or 0b11.")
        self.MODE_REG = m
        
    def set_ldac(self, ldac = 1):
        #check if mode allows for manual control
        if (self.MODE_REG == 3):
            #clear bit and set it
            self.CTRL_REG &= 0b0111
            print(self.CTRL_REG)
            self.CTRL_REG |= (ldac << 3)
            print(self.CTRL_REG)
        else:
            print("wrong mode (need to be in mode 3 to change ldac manually)")
            
    def set_clr(self, clr = 1):
        #WARNING THIS WILL  NOT STOP YOU FROM CLEARING EVEN IN THE MIDDLE OF A PVP PLOT
        self.CTRL_REG &= 0b1011
        self.CTRL_REG |= (clr << 2)
        
    def set_reset(self, resetn = 1):
        #WARNING THIS WILL  NOT STOP YOU FROM RESETTING EVEN IN THE MIDDLE OF A PVP PLOT
        self.CTRL_REG &= 0b1101
        self.CTRL_REG |= (resetn << 1)
            
    def report_settings(self):
        print("Start of DAC 0: ", hex(self.START_VAL_0_REG))
        print("Start of DAC 1: ", hex(self.START_VAL_1_REG))
        print("Start of DAC 2: ", hex(self.START_VAL_2_REG))
        print("Start of DAC 3: ", hex(self.START_VAL_3_REG))
        print("Control Reg: ", hex(self.CTRL_REG))
        print("Arbitrary 24 bits of SPI: ", hex(self.CONFIG_REG))
        print("Number of Dwell Cycles: ", hex(self.DWELL_CYCLES_REG))
        print("Cycles till Trigger AWGs: ", hex(self.CYCLES_TILL_READOUT))
        print("Step Size: ", hex(self.STEP_SIZE_REG))
        print("Size of PVP plot (square): ", hex(self.PVP_WIDTH_REG))
        print("Number of DACs Running: ", hex(self.NUM_DIMS_REG))
        print("DEMUX 0: ", hex(self.DEMUX_0_REG))
        print("DEMUX 1: ", hex(self.DEMUX_1_REG))
        print("DEMUX 2: ", hex(self.DEMUX_2_REG))
        print("DEMUX 3: ", hex(self.DEMUX_3_REG))
        
            
    def set_2D_pvp_parameters(self, start1, start2, demux1, demux2):
        self.check_lock("2D pvp parameters")
        self.set_start("0", start1)
        self.set_start("1", start2)
        self.set_demux("0", demux1)
        self.set_demux("1", demux2)
        
    def send_arbitrary_SPI(self, demux_int = 0b00000, reg = 0b0000, data_int = 0x00000):
        '''Lets the user specify an arbitrary dac (demux_int) and send it an arbitrary 24 bit message (data_int)
           Raises the done flag when finished and cannot be run again until pvp trigger reg is cleared'''
        
        self.check_lock("Arbitrary spi")
        
        demux_shift = demux_int << 24
        reg_shift = reg << 20
        out = demux_shift + reg_shift + data_int
        print("Writing config reg to " + str(bin(out)))
        self.CONFIG_REG = out
        time.sleep(0.1)
        self.CONFIG_REG = 0