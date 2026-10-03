package local.manametalchess;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.SidedProxy;
import cpw.mods.fml.common.event.FMLInitializationEvent;

@Mod(modid="manametalchessauto", name="魔法金属智慧试炼自动下棋", version="1.0.1",
        acceptedMinecraftVersions="[1.7.10]", acceptableRemoteVersions="*",
        dependencies="required-after:manametalmod")
public final class ChessAuto {
    @SidedProxy(clientSide="local.manametalchess.ClientProxy", serverSide="local.manametalchess.CommonProxy")
    public static CommonProxy proxy;
    @Mod.EventHandler public void init(FMLInitializationEvent event) { proxy.init(); }
}
