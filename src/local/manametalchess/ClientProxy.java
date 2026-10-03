package local.manametalchess;

import cpw.mods.fml.common.FMLCommonHandler;
import cpw.mods.fml.client.registry.ClientRegistry;
import cpw.mods.fml.relauncher.Side;
import cpw.mods.fml.relauncher.SideOnly;
import net.minecraftforge.common.MinecraftForge;

@SideOnly(Side.CLIENT)
public final class ClientProxy extends CommonProxy {
    private ClientHooks hooks;
    @Override public void init() {
        if(hooks!=null) return;
        hooks=new ClientHooks();
        FMLCommonHandler.instance().bus().register(hooks);
        MinecraftForge.EVENT_BUS.register(hooks);
        ClientRegistry.registerKeyBinding(hooks.toggle);
    }
}
