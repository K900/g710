import usb.core
import usb.util


class G710Context():
    def __enter__(self):
        self.device = usb.core.find(idVendor=0x046d, idProduct=0xc24d)

        if self.device:
            for interface in self.device.get_active_configuration():
                if interface.bInterfaceNumber == 1:
                    self.interface = interface
                    if self.device.is_kernel_driver_active(interface):
                        self.device.detach_kernel_driver(interface)

                    for endpoint in interface:
                        if endpoint.bEndpointAddress == 130:
                            self.endpoint = endpoint

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        usb.util.dispose_resources(self.device)
        self.device.attach_kernel_driver(self.interface)

