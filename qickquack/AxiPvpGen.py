from qick import SocIp
from .DACs import volt2reg
import time

class AxiPvpGen(SocIp):
    """Control the axi_pvp_gen_v7_x IP"""
    
    # PVP Gen Control Registers
    
    # START_VAL_0_REG : 20 bit
    # START_VAL_1_REG : 20 bit
    # START_VAL_2_REG : 20 bit
    # START_VAL_3_REG : 20 bit
    
    # STEP_SIZE_0_REG : 20 bit
    # STEP_SIZE_1_REG : 20 bit
    # STEP_SIZE_2_REG : 20 bit
    # STEP_SIZE_3_REG : 20 bit
    
    # DEMUX_0_REG : 5 bit 
    # DEMUX_1_REG : 5 bit
    # DEMUX_2_REG : 5 bit 
    # DEMUX_3_REG : 5 bit 
    
    # DAC_0_GROUP_REG: 2 bit
    # DAC_1_GROUP_REG: 2 bit
    # DAC_2_GROUP_REG: 2 bit
    # DAC_3_GROUP_REG: 2 bit
    
    # CTRL_REG: 4 bit
    # MODE_REG: 2 bit
    # CONFIG_REG: 29 bit
    
    # DWELL_CYCLES_REG = 32 bit
    # CYCLES_TILL_READOUT_REG = 16 bit
    # PVP_WIDTH_REG: 10 bit
    # NUM_DIMS_REG: 3 bit
    # TRIG_SRC_REG: 1 bit
    
    
    bindto = ['user.org:user:axi_pvp_gen_v7:4.0']
    
    def __init__(self, description, **kwargs):
        super().__init__(description)
        
        #map register names to offsets
        self.REGISTERS = {
            'START_VAL_0_REG':0, 
            'START_VAL_1_REG':1,
            'START_VAL_2_REG':2,
            'START_VAL_3_REG':3,
            
            'STEP_SIZE_0_REG':4,
            'STEP_SIZE_1_REG':5,
            'STEP_SIZE_2_REG':6,
            'STEP_SIZE_3_REG':7,
            
            'DEMUX_0_REG': 8,
            'DEMUX_1_REG': 9,
            'DEMUX_2_REG': 10,
            'DEMUX_3_REG': 11,
            
            'DAC_0_GROUP_REG': 12,
            'DAC_1_GROUP_REG': 13,
            'DAC_2_GROUP_REG': 14,
            'DAC_3_GROUP_REG': 15,
            
            'CTRL_REG': 16,
            'MODE_REG': 17,
            'CONFIG_REG': 18,
            
            'DWELL_CYCLES_REG': 19,
            'CYCLES_TILL_READOUT_REG': 20,
            'PVP_WIDTH_REG': 21,
            'NUM_DIMS_REG': 22,
            
            'TRIG_SRC_REG': 23
            
        }
        
        #default register values
        
        self.START_VAL_0_REG = 0
        self.START_VAL_1_REG = 0
        self.START_VAL_2_REG = 0
        self.START_VAL_3_REG = 0
        
        self.STEP_SIZE_0_REG = 0
        self.STEP_SIZE_1_REG = 0
        self.STEP_SIZE_2_REG = 0
        self.STEP_SIZE_3_REG = 0
        
        self.DEMUX_0_REG = 0 # if we don't set these, expect weird behavior on dac 0 when it tries to do it all
        self.DEMUX_1_REG = 0
        self.DEMUX_2_REG = 0
        self.DEMUX_3_REG = 0
        
        self.DAC_0_GROUP_REG = 0 # by default, assign one DAC per group
        self.DAC_1_GROUP_REG = 1
        self.DAC_2_GROUP_REG = 2
        self.DAC_3_GROUP_REG = 3
        
        
        self.CTRL_REG = 14
        self.MODE_REG = 0
        self.CONFIG_REG = 0
        
        self.DWELL_CYCLES_REG = 38400 # at board speed of 384 MHz, 38400 dwell cycles is 100 us
        self.CYCLES_TILL_READOUT = 10
        self.PVP_WIDTH_REG = 256
        self.NUM_DIMS_REG = 0
        
        self.TRIG_SRC_REG = 0 #default is 0 for trigger coming from qick, set for 1 for triggering manually for tests
        
        

    # ################################
    # Methods
    # ################################
   
        
    def check_lock(self, registerName = "<name of locked register>"):
        if (self.CTRL_REG & 0b1 == 1):
            raise RuntimeError (registerName + " cannot be changed while pvp plot is running.")
            
            
            
    ## Setters
    
    # many axis setters
    
    def set_any_axis(self, axis='', axis_reg_dict={}, val=0):
        '''helper method for any method that has four available axes'''
        
        if axis in axis_reg_dict:
            reg_str = axis_reg_dict[axis]
            setattr(self, reg_str, val)

        else:
            raise ValueError("No valid axis was specified. Valid axis arguments are '0', '1', '2', '3'")
    
    def set_start(self, axis = '', start_val = 0b00):
        '''method to set start val 
            (note that we want a method for this because we don't want to worry about registers outside this class)'''
        start_regs = {'0': 'START_VAL_0_REG', '1': 'START_VAL_1_REG', '2': 'START_VAL_2_REG', '3': 'START_VAL_3_REG'}
        self.check_lock("Start values")
        self.set_any_axis(axis = axis, axis_reg_dict = start_regs, val = start_val)
    
    def set_step_size(self, axis = '', step_size = 0):
        '''sets size of step (in Volts)'''
        step_size_regs = {'0': 'STEP_SIZE_0_REG', '1': 'STEP_SIZE_1_REG', '2': 'STEP_SIZE_2_REG', '3': 'STEP_SIZE_3_REG'}
        self.check_lock("step size")
        self.set_any_axis(axis = axis, axis_reg_dict = step_size_regs, val = step_size)
            
    def set_demux(self, axis = '', demux = 0):
        """Set demux value for a given axis"""
        self.check_lock("Demux values")
        demux_regs = {'0': 'DEMUX_0_REG', '1': 'DEMUX_1_REG', '2': 'DEMUX_2_REG', '3': 'DEMUX_3_REG'}
        
        #note to self: do we specify demux value or ask for board num and dac num?
        if (demux >= 0 and demux < 32):
            self.set_any_axis(axis = axis, axis_reg_dict = demux_regs, val = demux)
        else:
            raise ValueError("Demux value must be in the range 0-31 inclusive")
    
    def set_group(self, axis = '', group = 0):
        '''Set with which group a particular DAC should update'''
        group_regs = {'0': 'DAC_0_GROUP_REG', '1': 'DAC_1_GROUP_REG', '2': 'DAC_2_GROUP_REG', '3': 'DAC_3_GROUP_REG'}
        self.check_lock("groups")
        self.set_any_axis(axis = axis, axis_reg_dict = group_regs, val = group)
        
        
    #the next five are ctrl reg manipulating methods
    
    def set_ldac(self, ldac = 1):
        """Toggle the value of the LDAC pin, if in mode 3"""
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
        """Clear all DACs via CLRN pin"""
        #WARNING THIS WILL  NOT STOP YOU FROM CLEARING EVEN IN THE MIDDLE OF A PVP PLOT
        self.CTRL_REG &= 0b1011
        self.CTRL_REG |= (clr << 2)
        
    def set_reset(self, resetn = 1):
        """Reset all DACs via RSTN pin"""
        #WARNING THIS WILL  NOT STOP YOU FROM RESETTING EVEN IN THE MIDDLE OF A PVP PLOT
        self.CTRL_REG &= 0b1101
        self.CTRL_REG |= (resetn << 1)
        
    def start_pvp(self):
        """Start running a pvp plot"""
        if self.TRIG_SRC_REG == 1: #if in manual control mode
            self.CTRL_REG |= 0b1
        
    def pause_pvp(self):
        """Pause running a pvp plot but do not reset"""
        if self.TRIG_SRC_REG == 1:
            self.CTRL_REG &= 0b1110
        
    def end_pvp(self):
        """Stop running a pvp plot and reset"""
        if self.TRIG_SRC_REG == 1:
            self.CTRL_REG &= 0b1110
            self.set_reset(1) #
            self.set_reset(0)
        
    # regular registers
            
    def set_dwell_cycles(self, dwell_cycles = 38400):
        """Set number of clock cycles in between each step"""
        self.check_lock("Dwell cycles")
        if (dwell_cycles < 1250):
            raise ValueError("Dwell cycles must be at least 1250 so that all SPI messages can send")
        self.DWELL_CYCLES_REG = dwell_cycles
        
    def set_readout_cycles(self, cycles_till = 400):
        """Set number of cycles during which the measurement may be read out"""
        self.check_lock("Readout cycles")
        self.CYCLES_TILL_READOUT = cycles_till
    
        
    def set_pvp_width(self, pvp_width = 256): #this default value is so if someone accidentally runs the method without a argument, the new value is just the default reset value
        """Set the width in pixels of a pvp"""
        self.check_lock("Pvp width")
        self.PVP_WIDTH_REG = pvp_width
        
    def set_num_dims(self, num_dims = 0):
        """Set the number of groups looped through in the pvp plot"""
        self.check_lock("Number of dimensions")
        self.NUM_DIMS_REG = num_dims
                
    def set_mode(self, m = 0):
        """Set operation mode of the pvp gen block"""
        self.check_lock("Mode")
        if (m < 0 or m > 3):
            raise ValueError("Mode must be 0b00, 0b01, 0b10, or 0b11.")
        self.MODE_REG = m
        
    def set_trigger_source(self, src = 'qick'):
        if src == 'qick':
            self.TRIG_SRC_REG = 0
        elif src == 'user':
            self.TRIG_SRC_REG = 1
        else:
            raise ValueError("Trigger source must be either 'qick' or 'user'")
        
    # we don't ever just set the config reg so it's not in the simple setters- see next section
    
    ## Compound methods
            
    def report_settings(self):
        """Report all pvp gen registers' current value"""
        print("Start of DAC 0: ", hex(self.START_VAL_0_REG))
        print("Start of DAC 1: ", hex(self.START_VAL_1_REG))
        print("Start of DAC 2: ", hex(self.START_VAL_2_REG))
        print("Start of DAC 3: ", hex(self.START_VAL_3_REG))
        
        print("Step Size DAC 0: ", hex(self.STEP_SIZE_0_REG))
        
        print("DEMUX 0: ", hex(self.DEMUX_0_REG))
        print("DEMUX 1: ", hex(self.DEMUX_1_REG))
        print("DEMUX 2: ", hex(self.DEMUX_2_REG))
        print("DEMUX 3: ", hex(self.DEMUX_3_REG))
        
        print("Control Reg: ", hex(self.CTRL_REG))
        print("Mode Reg", hex(self.MODE_REG))
        print("Arbitrary 24 bits of SPI: ", hex(self.CONFIG_REG))
        
        print("Number of Dwell Cycles: ", hex(self.DWELL_CYCLES_REG))
        print("Cycles till Trigger AWGs: ", hex(self.CYCLES_TILL_READOUT))
        print("Size of PVP plot (square): ", hex(self.PVP_WIDTH_REG))
        print("Number of DACs Running: ", hex(self.NUM_DIMS_REG))
        print("Trigger source: ", "user" if (self.TRIG_SRC_REG) else "qick_processor")
       
        
    def send_arbitrary_SPI(self, demux_int = 0b00000, reg = 0b0000, data_int = 0x00000):
        '''Allow the user to specify an arbitrary dac (demux_int) and send it an arbitrary 24 bit message (data_int)
           Raises the done flag when finished and cannot be run again until pvp trigger reg is cleared'''
        
        self.check_lock("Arbitrary spi")
        
        demux_shift = demux_int << 24
        reg_shift = reg << 20
        out = demux_shift + reg_shift + data_int
        print("Writing config reg to " + str(bin(out)))
        self.CONFIG_REG = out
        time.sleep(0.1)
        self.CONFIG_REG = 0
        
    def setup_pvp(self, cfg = {'startvals': [0,0,0,0],
                              'stepsizes': [0,0,0,0],
                              'demuxvals': [0,0,0,0],
                                'groups': [0,1,2,3],
                                 'mode': 0,
                               'width': 16,
                               'num_dims': 4
                              }
                 ):
        '''sets up EVERYTHING for a pvp plot
        assuming a user sets everything they want here, they should only need to run this + start_pvp()'''
        
        for dac in range (len(cfg['startvals'])):
            self.set_start(axis = str(dac), start_val = volt2reg(cfg['startvals'][dac]))
            self.set_step_size(axis = str(dac), step_size = volt2reg(cfg['stepsizes'][dac]))
            self.set_demux(axis = str(dac), demux = cfg['demuxvals'][dac])
            self.set_group(axis = str(dac), group = cfg['groups'][dac])
        self.set_mode(cfg['mode'])
        self.set_pvp_width(cfg['width'])
        self.set_num_dims(cfg['num_dims'])
