package xyz.misilelaboratory.hardflat

import io.papermc.paper.event.player.PrePlayerAttackEntityEvent
import org.bukkit.Material
import org.bukkit.enchantments.Enchantment
import org.bukkit.entity.LivingEntity
import org.bukkit.entity.Player
import org.bukkit.event.EventHandler
import org.bukkit.event.Listener
import org.bukkit.event.block.BlockBreakEvent
import org.bukkit.event.entity.EntityDamageByEntityEvent
import org.bukkit.event.entity.EntityDamageEvent
import org.bukkit.event.entity.EntityShootBowEvent
import org.bukkit.event.entity.PlayerDeathEvent
import org.bukkit.event.inventory.CraftItemEvent
import org.bukkit.event.player.PlayerItemConsumeEvent
import org.bukkit.inventory.ItemStack
import org.bukkit.plugin.java.JavaPlugin

@Suppress("unused")
class HardFlat: JavaPlugin() {
    override fun onEnable() {
        this.logger.info("Enabled plugin")
        this.server.pluginManager.registerEvents(EHandler(), this)
    }
}

class EHandler: Listener {

    private val rawFood = listOf(Material.PORKCHOP, Material.BEEF, Material.CHICKEN, Material.MUTTON, Material.RABBIT,
        Material.COD, Material.SALMON)

    @EventHandler
    fun onDamage(e: EntityDamageEvent) {
        if (e is LivingEntity) {
            val ent = e as LivingEntity
            ent.noDamageTicks = 0
        }
    }

    @EventHandler
    fun onPlayerDamageToEntity(e: EntityDamageByEntityEvent) {
        if (e.entity is Player) {
            val ent = e.entity as Player
            if (ent.isBlocking) {
                if ((1..20).random() == 20) {
                    ent.shieldBlockingDelay = 100
                    ent.clearActiveItem()
                    ent.sendMessage("shield breaked lol")
                }
            }
        } else if (e.damager is Player) {
            if ((1..10).random() == 0) {
                e.isCancelled = true
            }
        }
    }

    @EventHandler
    fun onBreak(e: BlockBreakEvent) {
        val rand = (1..20).random()
        if (rand >= 19) {
            e.isCancelled = true
            e.player.sendMessage("you breaked air lol")
        } else if (rand == 1) {
            e.isDropItems = false
            e.player.sendMessage("no item")
        }
    }

    @EventHandler
    fun onDeath(e: PlayerDeathEvent) {
        for (i in e.drops) {
            if (!i.enchantments.containsKey(Enchantment.VANISHING_CURSE)) {
                i.addUnsafeEnchantment(Enchantment.VANISHING_CURSE, 1)
            }
        }
    }

    @EventHandler
    fun onAttack(e: PrePlayerAttackEntityEvent) {
        if (e.player.attackCooldown != (0).toFloat()) {
            e.isCancelled = true
            e.player.sendMessage("no attack because has attack cooldown lol")
        }
    }

    @EventHandler
    fun onBowAttack(e: EntityShootBowEvent) {
        if (e.entity is Player) {
            val p = e.entity as Player
            if (p.attackCooldown != (0).toFloat()) {
                e.isCancelled = true
                p.sendMessage("no attack because has attack cooldown lol")
            }
        }
    }

    @EventHandler
    fun onCrafting(e: CraftItemEvent) {
        if ((1..100).random() == 1) {
            e.isCancelled = true
        } else if ((1..100).random() == 1) {
            e.inventory.result = ItemStack(Material.AIR)
            e.inventory.clear()
        }
    }

    @EventHandler
    fun onFoodEat(e: PlayerItemConsumeEvent) {
        if ((1..20).random() == 1) {
            e.isCancelled = true
        } else if (e.item.type in rawFood) {
            e.player.damage((6).toDouble())
        }
    }
}