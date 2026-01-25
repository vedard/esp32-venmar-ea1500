class MCP41X1:
    """
    Microchip MCP41X1 – Digital Potentiometer (SPI)

    Datasheet:
    https://ww1.microchip.com/downloads/en/DeviceDoc/22059b.pdf
    """
    WIPER_ADDRESS = 0b0000
    WRITE_COMMAND = 0b00
    INCREMENT_COMMAND = 0b01
    DECREMENT_COMMAND = 0b10

    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        

    def __send_16bit_command(self, command, value):
        """
        Send a 16-bit command (used for Read Data and Write Data commands).
        """

        self.cs.off()
        try:
            self.spi.write(bytes([
                # 0000   00        0        000000000
                # wiper  command   unused   9bit value
                self.WIPER_ADDRESS << 4 | command << 2 | value >> 8,
                value & 0xff
            ]))
            return True
        except Exception:
            print("Could not send command to MCP41X1")
            return False
        finally:
            self.cs.on()

    def __send_8bit_command(self, command, value):
        """
        Send a 8-bit command (used for Increment Wiper and Decre-ment Wiper command).
        """

        self.cs.off()
        try:
            self.spi.write(bytes([
                # 0000   00        00        
                # wiper  command   2bit value 
                self.WIPER_ADDRESS << 4 | command << 2 | (value & 0b11)
            ]))
            return True
        except Exception:
            print("Could not send command to MCP41X1")
            return False
        finally:
            self.cs.on()

    def wiper_write(self, value):
        """
        Set the wiper position.

        :param value: 0-255
        """
        if not 0 <= value < 256:
            raise ValueError("Wiper value must be 0–255")
        
        print(f"Setting MCP41X1 wiper to '{value}'")
        return self.__send_16bit_command(self.WRITE_COMMAND, value)

    def wiper_increment(self):
        """
        Increment wiper by one step.
        """
        return self.__send_8bit_command(self.INCREMENT_COMMAND, 0)

    
    def wiper_decrement(self):
        """
        Decrement wiper by one step.
        """
        return self.__send_8bit_command(self.DECREMENT_COMMAND, 0)