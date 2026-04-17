package ru.scp.myapplication

import android.app.Application
import ru.scp.myapplication.core.di.AppContainer

class ToirApplication : Application() {

    lateinit var appContainer: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        appContainer = AppContainer(this)
    }
}
