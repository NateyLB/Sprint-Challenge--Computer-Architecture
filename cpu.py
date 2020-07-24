"""CPU functionality."""

import sys
from datetime import datetime
IS = 6
SP = 7
HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
JMP = 0b01010100
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
PRA = 0b01001000
LD = 0b10000011
INC = 0b01100101
DEC = 0b01100110
ST = 0b10000100
IRET = 0b00010011
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] =  0b11110100
        self.ir = 0
        self.pc = 0
        self.fl = 0b00000000
        self.bt = {}
        self.bt[HLT] = self.handle_HLT
        self.bt[PRN] = self.handle_PRN
        self.bt[LDI] = self.handle_LDI
        self.bt[ADD] = self.handle_ADD
        self.bt[MULT] = self.handle_MULT
        self.bt[PUSH] = self.handle_PUSH
        self.bt[POP] = self.handle_POP
        self.bt[CALL] = self.handle_CALL
        self.bt[RET] = self.handle_RET
        self.bt[JMP] = self.handle_JMP
        self.bt[CMP] = self.handle_CMP
        self.bt[JEQ] = self.handle_JEQ
        self.bt[JNE] = self.handle_JNE
        self.bt[PRA] = self.handle_PRA
        self.bt[LD] = self.handle_LD
        self.bt[INC] = self.handle_INC
        self.bt[DEC] = self.handle_DEC
        self.bt[ST] = self.handle_ST
        self.bt[IRET] = self.handle_IRET

    def load(self):
        """Load a program into memory."""

        address = 0

        # get file from sys.args and populate program
        file = open(sys.argv[1], "r")
        
        program = []
        for curline in file:
            if curline.startswith('#') or curline == '\n':
                continue
            else:
                split = curline.split(' ', 1)
                split[0] = split[0].strip()
                if len(split) > 1:
                    split[1] = split[1].strip()
                program.append(int(split[0], base=2))
        for instruction in program:
            self.ram[address] = instruction
            address += 1
        # print(self.ram, "ram")

    def ram_read(self,MAR):
        """ read value at memory address """
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        """ write value at memory address"""
        self.ram[MAR] = MDR
    

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_HLT(self):
        ## HALT
        self.running = False

    def handle_PRN(self):
        ## PRN print value in giver register
        reg = self.ram_read(self.pc + 1)
        print(self.reg[reg])
        self.pc += 2

    def handle_LDI(self):
        ## LDI set register to value
        reg = self.pc + 1
        val = self.pc + 2
        self.reg[self.ram_read(reg)] = self.ram_read(val)
        self.pc += 3

    def handle_ADD(self):
        ## ADD reagA and regB, store results in regA
        self.alu("ADD",self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
        self.pc += 3

    def handle_MULT(self):
        ## MULT regA and regB together, store esults in regA
        self.alu("MULT",self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
        self.pc += 3
    
    def handle_CMP(self):
        ## CMP regA and regB and set the FL reg corresondingly
        self.alu("CMP",self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
        self.pc += 3

    def handle_INC(self):
        self.alu("INC", self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
        self.pc += 2

    def handle_DEC(self):
        self.alu("DEC", self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
        self.pc += 2
    
    def handle_PUSH(self):
        ## PUSH instruction from register onto STACK
        self.reg[SP] -= 1
        self.ram_write(self.reg[self.ram_read(self.pc + 1)], self.reg[SP])
        self.pc += 2

    def handle_POP(self):
        ## POP instruction from stack onto register
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        self.pc += 2  
    
    def handle_RET(self):
        # print(self.ram_read(self.reg[SP]))
        self.pc = self.ram_read(self.reg[SP])
        # self.subroutine = False
        self.reg[SP] += 1

    def handle_CALL(self):
        #Calls a subroutine at the address stored in register
        address = self.pc + 2
        self.reg[SP] -= 1
        ## Store address of next instruction in stack
        self.ram_write(address, self.reg[SP])
        self.pc = self.reg[self.ram_read(self.pc + 1)]

        # self.subroutine = True
        # while self.subroutine:
        #     self.ir = self.ram_read(self.pc)
        #     self.bt[self.ir]()
    def handle_JMP(self):
        ## jump to address in register
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def handle_JEQ(self):
        ## if FL E flag is on, jump
        if self.fl == 0b00000001:
            self.handle_JMP()
        else:
            self.pc += 2
    
    def handle_JNE(self):
        if self.fl != 0b00000001:
            self.handle_JMP()
        else:
            self.pc += 2
    
    def handle_PRA(self):
        ##Print ASCII character in register
        print(chr(self.reg[self.ram_read(self.pc + 1)]), end='')
        self.pc += 2

    def handle_LD(self):
        ##loads register A with the value store at the memeory accress in regB
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.reg[self.ram_read(self.pc + 2)])
        self.pc += 3
    
    def handle_ST(self):
        ## Store value in registerB in the address stored in registerA

        self.ram_write(self.reg[self.ram_read(self.pc + 2)],self.reg[self.ram_read(self.pc + 1)])
        self.pc += 3
    
    def handle_IRET(self):
        for index in range(6,-1, -1):
            self.reg[index] = self.ram_read(self.reg[SP])
            self.reg[SP] -= 1
        self.pc = self.ram_read(self.reg[SP])
        self.reg[IS] = 0

    def run(self):
        """Run the CPU."""

        self.running = True
        self.time = datetime.now()
        while self.running:
            ## comment out betwwen ## to disable timmer interrupt
            if self.reg[IS] == 1:
                self.time = datetime.now()
                self.reg[SP] -= 1
                self.ram_write(self.pc, self.reg[SP])
                for index in range(7):
                    self.reg[SP] -= 1
                    self.ram_write(self.reg[index], self.reg[SP])
                self.pc = self.ram_read(0xF8)
                print()
                while self.reg[IS] == 1:
                    self.ir = self.ram_read(self.pc)
                    self.bt[self.ir]()
            ######################################################        

            self.ir = self.ram_read(self.pc)
            self.bt[self.ir]()

            ######################################################
            now = datetime.now()
            elapsed = now - self.time
            if elapsed.total_seconds() > 1:
                self.reg[IS] = 1
            #######################################################        
    
    

